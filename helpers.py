# flask
from flask import (
    redirect, url_for, session as login_session, make_response )
# general
from functools import wraps
import json


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
