# add database directory to python modules path.
import sys
sys.path.append("./database/")

# flask
from flask import (
    redirect, url_for, session as login_session, make_response )
# general
from functools import wraps
import json
# database
from db_session import session, Restaurant, MenuItem, User


def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not login_session.get('user_id'):
            return redirect(url_for('login_management.login'))
        return f(*args, **kwargs)
    return decorated_function


def json_mime_response(response_body, status_code):
    """
    args: response_body, status_code
      response_body: string message to write in response body
    returns: response object of json mimetype
    """
    response = make_response(json.dumps(response_body), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response


def create_user(login_session):
    """creates a new user based on login_session info. and returns his id"""
    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_id(email):
    """returns user_id if email exists in DB, else None"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_permissions(user_id, restaurant_or_item):
    """
    returns two boolean values, the first indicates if user is logged in,
    the second indicates if he is the owner of restaurant_or_item object.
    """
    is_app_user = True if user_id else False 
    return is_app_user , user_id==restaurant_or_item.user_id
