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
import httplib2
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


# get client id client_secrets file that access token will be issued to
CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']


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
        # new method
        credentials_obj = client.credentials_from_clientsecrets_and_code(
            'client_secrets.json',
            ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
            auth_code)
        # lesson method:
        # oauth_flow_obj = client.flow_from_clientsecrets('client_secrets.json', scope='')
        # oauth_flow_obj.redirect_uri = 'postmessage' # confirm it is one-time-auth-code
        # credentials_obj = oauth_flow_obj.step2_exchange(auth_code) # initiate exchange
    except client.FlowExchangeError:
        return json_mime_response('Failed to upgrade the authorization code', 401)

    # Access token tests:
    # Verify access token is valid
    access_token = credentials_obj.access_token
    url = f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}'
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error'):
        return json_mime_response(result.get('error'), 500)
    # Verify access token is used for the intended user.
    user_id_from_credentials = credentials_obj.id_token['sub']
    if result['user_id'] != user_id_from_credentials:
        return json_mime_response("Token's user ID doesn't match given user ID.", 401)
    # Verify access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
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

    # Check user is already logged out
    if not login_session.get('user_id'):
        return json_mime_response('Current user not connected.', 401)

    # make a request to revoke token 
    url = f"https://accounts.google.com/o/oauth2/revoke?token={login_session['access_token']}"
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # r = requests.post('https://accounts.google.com/o/oauth2/revoke',
    #     params={'token': login_session.get('access_token')},
    #     headers = {'content-type': 'application/x-www-form-urlencoded'})
    # result = r.json()
    # see https://stackoverflow.com/a/54260972

    # revoke access token
    if result.get('status') == '200':
        login_session.clear() # https://stackoverflow.com/q/27747578
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
    short_lived_token = request.data.decode("utf-8")
    # converted from bytes obj to str to plug into next url

    # Exchange short_lived_token with a long_lived_token
    app_id_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']
    app_id = app_id_secret['app_id']
    app_secret = app_id_secret['app_secret']

    print()
    print(f"short_lived_token = {short_lived_token}")
    print(f"app id = {app_id}")
    print(f"app secret = {app_secret}")
    print()

    url = f"""https://graph.facebook.com/oauth/access_token?client_id={app_id}&client_secret={app_secret}&grant_type=fb_exchange_token&fb_exchange_token={short_lived_token}"""
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    long_lived_token = result.get('access_token')
    
    print()
    print(f"exchange result = {result}")
    print(f"long_lived_token = {long_lived_token}")
    print()

    # get user's name,id,email from API
    url = f"""https://graph.facebook.com/v3.2/me?access_token={long_lived_token}&fields=name,id,email"""
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    
    print()
    print(f"user info = {result}")
    print()

    # Store credentials in session for later use.
    login_session['provider'] = 'facebook'
    login_session['access_token'] = long_lived_token
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['fb_id'] = data['id']
    
    # get user's picture from API
    url = f"""https://graph.facebook.com/v3.2/me/picture?access_token={long_lived_token}&redirect=0&height=200&width=200"""
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    print()
    print(f"user picture = {result}")
    print()

    login_session['picture'] = data['data']['url']
    
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

    # make a request to revoke token 
    url = f"https://graph.facebook.com/{login_session['fb_id']}/permissions?access_token={login_session['access_token']}"
    h = httplib2.Http()
    result = json.loads(h.request(url, 'DELETE')[1])
    
    print()
    print(f"disconnect result = {result}")
    print()

    # revoke access token
    if result.get('success') == True:
        login_session.clear() # https://stackoverflow.com/q/27747578
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