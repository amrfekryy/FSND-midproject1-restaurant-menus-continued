# add database directory to python modules path.
import sys
sys.path.append("./database/")

# flask
from flask import ( 
    Blueprint, render_template, request, flash, 
    session as login_session )
# templates have direct access to the session obj, but as 'session' not the alias.

# general
import random, string
from oauth2client import client
import json
import requests
from helpers import *
# database
from db_session import session, Restaurant, MenuItem, User


# create blueprint
# http://flask.pocoo.org/docs/1.0/blueprints/
login_management = Blueprint('login_management', __name__,
                     template_folder='templates', 
                     static_folder='static')


# get client ids/secrets from external json files
G_CLIENT_ID = json.loads(open('g_client_secrets.json','r').read())['web']['client_id']
fb_app_credentials = json.loads(open('fb_client_secrets.json', 'r').read())['web']
FB_APP_ID = fb_app_credentials['app_id']
FB_APP_SECRET = fb_app_credentials['app_secret']


@login_management.route('/login/')
def login():
    # create anti-forgery state token
    state_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state_token'] = state_token
    # return f"Current session state token in {login_session.get('state_token')}"
    return render_template('login.html', state_token=state_token)


@login_management.route('/gconnect', methods=['POST'])
def gconnect():
    
    # Check state_token to protect against CSRF
    if request.args.get('state_token') != login_session['state_token']:
        return json_mime_response('Invalid state token parameter', 401)

    # Check user is already logged in
    if login_session.get('user_id'):
        return json_mime_response('Current user is already connected.', 200)    
    
    # Collect one-time-auth-code from request
    auth_code = request.data

    # Exchange auth code for credentials obj containing access token, refresh token, and ID token
    try:
        credentials_obj = client.credentials_from_clientsecrets_and_code(
            'g_client_secrets.json',
            ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
            auth_code)
        print(f"ACCESS TOKEN = {credentials_obj.access_token}")
    except client.FlowExchangeError:
        return json_mime_response('Failed to upgrade the authorization code', 401)

    # get token information from access token:
    r = requests.get(
        url="https://www.googleapis.com/oauth2/v1/tokeninfo",
        params={'access_token': credentials_obj.access_token})
    token_info = r.json()
    # print(f"RESPONSE KEYS = {token_info.keys()}")
    # Verify access token is valid
    if token_info.get('error'):
        return json_mime_response(token_info.get('error'), 500)
    # Verify access token is used for the intended user.
    user_id_from_credentials = credentials_obj.id_token['sub']
    if token_info.get('user_id') != user_id_from_credentials:
        return json_mime_response("Token's user ID doesn't match given user ID.", 401)
    # Verify access token is valid for this app.
    if token_info.get('issued_to') != G_CLIENT_ID:
        return json_mime_response("Token's client ID does not match app's.", 401)


    # Access token tests passed:
    # Store credentials in session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials_obj.access_token
    login_session['username'] = credentials_obj.id_token['name']
    login_session['picture'] = credentials_obj.id_token['picture']
    login_session['email'] = credentials_obj.id_token['email']
    
    # Create new user if not existant
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    flash(f"you are now logged in as {login_session['username']}")
    
    # return successful response to client-side ajax request   
    return f"""
        <h1>Welcome, {login_session['username']}!</h1>
        <img src="{login_session['picture']}" style = "width:60px; height:60px; border-radius:30px; -webkit-border-radius:30px; -moz-border-radius:30px;">
    """


@login_management.route('/gdisconnect')
def gdisconnect():

    # Check user is not logged in
    if not login_session.get('user_id'):
        return json_mime_response('Current user not connected.', 401)

    # revoke access token
    # see https://developers.google.com/identity/protocols/OAuth2WebServer
    r = requests.post(
        url='https://accounts.google.com/o/oauth2/revoke',
        params={'token': login_session.get('access_token')},
        headers = {'content-type': 'application/x-www-form-urlencoded'})    # 
    # successful disconnect returns 200 OK status code
    if r.status_code == 200:
        login_session.clear() # https://stackoverflow.com/q/27747578
        flash("You have logged out successfully")
        return json_mime_response('Successfully disconnected.', 200)
    else:
        return json_mime_response('Failed to revoke token for given user.', 400)


@login_management.route('/fbconnect', methods=['POST'])
def fbconnect():
    
    # Check state_token to protect against CSRF
    if request.args.get('state_token') != login_session['state_token']:
        return json_mime_response('Invalid state token parameter', 401)

    # Check user is already logged in
    if login_session.get('user_id'):
        return json_mime_response('Current user is already connected.', 200)
    
    # Collect short-lived access token from request
    short_lived_token = request.data

    # Exchange short_lived_token with a long_lived_token
    r = requests.get(
        url="https://graph.facebook.com/oauth/access_token",
        params={
        'client_id': FB_APP_ID,
        'client_secret': FB_APP_SECRET,
        'grant_type': 'fb_exchange_token',
        'fb_exchange_token': short_lived_token})
    long_lived_token = r.json().get('access_token')

    # Get user's name, id, email from API
    r = requests.get(
        url="https://graph.facebook.com/v3.2/me",
        params={
        'access_token': long_lived_token,
        'fields': 'name,id,email'})
    user_info = r.json()
    # Store user info in session for later use.
    login_session['provider'] = 'facebook'
    login_session['access_token'] = long_lived_token
    login_session['username'] = user_info.get('name')
    login_session['email'] = user_info.get('email')
    login_session['fb_id'] = user_info.get('id')
    
    # Get user's picture from API
    r = requests.get(
        url="https://graph.facebook.com/v3.2/me/picture",
        params={
        'access_token': long_lived_token,
        'redirect': '0',
        'height': '200',
        'width': '200'})
    # Store user picture in session for later use.
    login_session['picture'] = r.json()['data']['url']
    
    # Create new user if not existant
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    flash(f"you are now logged in as {login_session['username']}")
    
    # return successful response to client-side ajax request   
    return f"""
        <h1>Welcome, {login_session['username']}!</h1>
        <img src="{login_session['picture']}" style = "width:60px; height:60px; border-radius:30px; -webkit-border-radius:30px; -moz-border-radius:30px;">
    """


@login_management.route('/fbdisconnect')
def fbdisconnect():

    # Check user is already logged out
    if not login_session.get('user_id'):
        return json_mime_response('Current user not connected.', 401)

    # revoke long lived token 
    r = requests.delete(
        url=f"https://graph.facebook.com/{login_session.get('fb_id')}/permissions",
        params={'access_token': login_session.get('access_token')})
    
    # successful disconnect returns {"success":true}
    if r.json().get('success') == True:
        login_session.clear() # https://stackoverflow.com/q/27747578
        flash("You have logged out successfully")
        return json_mime_response('Successfully disconnected.', 200)
    else:
        return json_mime_response('Failed to revoke token for given user.', 400)



@login_management.route('/disconnect')
def disconnect():
    provider = login_session.get('provider')
    if provider:
        if provider == 'google':
            return redirect(url_for('.gdisconnect'))
        if provider == 'facebook':
            return redirect(url_for('.fbdisconnect'))
    else:
        # flash("You are not logged in!")
        return json_mime_response('Current user not connected.', 401)
