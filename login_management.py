
# flask
from flask import ( 
    Blueprint, render_template, request, flash, 
    session as login_session )
# general
import random, string
from oauth2client import client
import httplib2
import json
import requests
from helpers import *


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
    
    # Collect one-time-auth-code from request
    auth_code = request.data

    # Exchange auth code for credentials obj containing access token, refresh token, and ID token
    try:
        # new method
        credentials_obj = client.credentials_from_clientsecrets_and_code(
            'client_secrets.json',
            ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
            auth_code)
        print(credentials_obj.access_token)
        # lesson method:
        # oauth_flow_obj = client.flow_from_clientsecrets('client_secrets.json', scope='')
        # oauth_flow_obj.redirect_uri = 'postmessage' # confirm it is one-time-auth-code
        # credentials_obj = oauth_flow_obj.step2_exchange(auth_code) # initiate exchange
    except client.FlowExchangeError:
        return json_mime_response('Failed to upgrade the authorization code', 401)

    # Check access token is valid
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
    # Check user is already logged in
    if login_session.get('access_token'):
        return json_mime_response('Current user is already connected.', 200)

    # After passing above verifications:
    # Store credentials in session for later use.
    login_session['access_token'] = credentials_obj.access_token
    login_session['user_id'] = credentials_obj.id_token['sub']
    login_session['username'] = credentials_obj.id_token['name']
    login_session['picture'] = credentials_obj.id_token['picture']
    login_session['email'] = credentials_obj.id_token['email']

    flash(f"you are now logged in as {login_session['username']}")
    
    # return successful response to client-side ajax request   
    return f"""
        <h1>Welcome, {login_session['username']}!</h1>
        <img src="{login_session['picture']}" style = "width:300px; height:300px; border-radius:150px; -webkit-border-radius:150px; -moz-border-radius:150px;">
    """


@login_management.route('/gdisconnect')
def gdisconnect():

    # Verify user is already logged in
    access_token = login_session.get('access_token')
    if access_token is None:
        return json_mime_response('Current user not connected.', 401)

    # make a request to revoke token 
    # url = f"https://accounts.google.com/o/oauth2/revoke?token={login_session['access_token']}"
    # h = httplib2.Http()
    # result = h.request(url, 'GET')[0]
    r = requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': login_session['access_token']},
        headers = {'content-type': 'application/x-www-form-urlencoded'})
    result = r.json()
    print(login_session['access_token'])
    print(result)
    if result.get('status') == '200' or result.get('error') == 'invalid_token':
        login_session.clear() # https://stackoverflow.com/q/27747578
        return json_mime_response('Successfully disconnected.', 200)
    else:
        return json_mime_response('Failed to revoke token for given user.', 400)

