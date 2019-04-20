
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.db_setup import Base, Restaurant, MenuItem

from flask import session as login_session
import random, string

# from apiclient import discovery
from oauth2client import client
import httplib2
import json
from flask import make_response
import requests

# get client id from client_secrets.json
CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']

# connect to DB and DB tables
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
# establish 'session' connection for CRUD executions
session = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

# clear orm session after each request
@app.teardown_request
def remove_session(ex=None):
    session.remove()
# https://stackoverflow.com/a/34010159
# https://stackoverflow.com/q/30521112


@app.route('/login/')
def login():
    # create anti-forgery state token
    state_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state_token'] = state_token
    # return f"Current session state token in {login_session.get('state_token')}"
    return render_template('login.html', state_token=state_token)


# https://developers.google.com/identity/sign-in/web/server-side-flow
@app.route('/gconnect', methods=['POST'])
def gconnect():
    
    # Check state_token to protect against CSRF
    if request.args.get('state_token') != login_session['state_token']:
        # create a response object manually and attach a header
        response = make_response(json.dumps('Invalid state token parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Collect one-time-auth-code from request
    auth_code = request.data
    print(auth_code)

    # Exchange auth code for credentials obj containing access token, refresh token, and ID token
    try:
        oauth_flow_obj = client.flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow_obj.redirect_uri = 'postmessage' # confirm it is one-time-auth-code
        credentials_obj = oauth_flow_obj.step2_exchange(auth_code) # initiate exchange
    except client.FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check access token is valid
    access_token = credentials_obj.access_token
    url = f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}'
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify access token is used for the intended user.
    user_id_from_credentials = credentials_obj.id_token['sub']
    if result['user_id'] != user_id_from_credentials:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_user_id = login_session.get('user_id')
    if stored_access_token is not None and user_id_from_credentials == stored_user_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # After passing above verifications:
    # Store credentials if in session for later use.
    login_session['access_token'] = credentials_obj.access_token
    login_session['user_id'] = user_id_from_credentials

    # Get some user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials_obj.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash(f"you are now logged in as {login_session['username']}")

    return output



@app.route('/')
@app.route('/restaurants/')
def index():

    restaurants_list = session.query(Restaurant).all()
    return render_template('index.html', restaurants_list=restaurants_list)


@app.route('/restaurants/add/', methods=['GET', 'POST'])
def add_restaurant():
    
    if request.method == 'POST':

        restaurant_name = request.form.get('restaurant_name')
        if restaurant_name:

            new_restaurant = Restaurant(name=restaurant_name)
            session.add(new_restaurant)
            session.commit()
            flash(f"New restaurant \"{restaurant_name}\" has been added")
            return redirect(url_for('index'))
        else:
            return "Name field is empty!"
    
    else:
        return render_template('add_restaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    
    if request.method == 'POST':

        restaurant_new_name = request.form.get('restaurant_new_name')
        if restaurant_new_name:

            restaurant.name = restaurant_new_name
            session.add(restaurant)
            session.commit()
            flash(f"Restaurant \"{restaurant_new_name}\" has been edited")
            return redirect(url_for('index'))
        else:
            return "You haven't entered a name!"
    
    else:
        return render_template('edit_restaurant.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    restaurant_name = restaurant.name

    if request.method == 'POST':

        answer = request.form.get('answer')
        if answer == 'yes':
            session.delete(restaurant)
            session.commit()
            flash(f"Restaurant \"{restaurant_name}\" has been deleted")
            return redirect(url_for('index'))
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    
    else:
        return render_template('delete_restaurant.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurant_menu(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    return render_template('restaurant_menu.html', restaurant=restaurant, menu_items=menu_items)


@app.route('/restaurants/<int:restaurant_id>/menu/add', methods=['GET', 'POST'])
def add_menu_item(restaurant_id):

    if request.method == 'POST':

        item_name = request.form.get('item_name')
        item_price = request.form.get('item_price')
        item_description = request.form.get('item_description')
        item_course = request.form.get('item_course')
        if item_name and item_price and item_description and item_course:

            new_item = MenuItem(name=item_name, price=item_price, description=item_description, course=item_course, restaurant_id=restaurant_id)
            session.add(new_item)
            session.commit()
            flash(f"New item \"{item_name}\" has been added")
            return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
        else:
            return "One or more fields is empty!"
    
    else:
        return render_template('add_menu_item.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, item_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id=item_id).one()

    if request.method == 'POST':

        item_new_name = request.form.get('item_new_name')
        item_new_price = request.form.get('item_new_price')
        item_new_description = request.form.get('item_new_description')
        item_new_course = request.form.get('item_new_course')

        if item_new_name: menu_item.name = item_new_name
        if item_new_price: menu_item.price = item_new_price
        if item_new_description: menu_item.description = item_new_description
        if item_new_course: menu_item.course = item_new_course
        
        session.add(menu_item)
        session.commit()
        flash(f"Item \"{menu_item.name}\" has been edited")
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    
    else:
        return render_template('edit_menu_item.html', restaurant=restaurant, menu_item=menu_item)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, item_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id=item_id).one()
    item_name = menu_item.name

    if request.method == 'POST':

        answer = request.form.get('answer')
        if answer == 'yes':
            session.delete(menu_item)
            session.commit()
            flash(f"Item \"{item_name}\" has been deleted")

        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    
    else:
        return render_template('delete_menu_item.html', restaurant=restaurant, menu_item=menu_item)


# ~~~~~~~~ API ENDPOINTS:

@app.route('/api/')
def api():
    return render_template('api.html')


@app.route('/api/restaurants/')
def api_restaurants():
    restaurants_list = session.query(Restaurant).all()

    list_of_dicts = []
    for restaurant in restaurants_list:
        restaurant_dict = {
            'restaurant_id':restaurant.id,
            'restaurant_name':restaurant.name,
        }
        list_of_dicts.append(restaurant_dict)
    
    return jsonify({'restaurants':list_of_dicts})


@app.route('/api/restaurant/<int:restaurant_id>/')
def api_restaurant(restaurant_id):
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    except:
        return f"There is no restaurant with id = {restaurant_id}"

    restaurant_dict = {
        'restaurant_id':restaurant.id,
        'restaurant_name':restaurant.name,
        'restaurant_menu':[item.serialize for item in menu_items]
    }
    return jsonify(restaurant_dict)


@app.route('/api/menu_item/<int:item_id>/')
def api_menu_item(item_id):
    try:
        menu_item = session.query(MenuItem).filter_by(id=item_id).one()
    except:
        return f"There is no item with id = {item_id}"

    restaurant = session.query(Restaurant).filter_by(id=menu_item.restaurant_id).one()

    item_dict = {
        'restaurant_id':restaurant.id,
        'restaurant_name':restaurant.name,
        'menu_item':menu_item.serialize
    }
    return jsonify(item_dict)


@app.route('/api/all/')
def api_all():
    restaurants_list = session.query(Restaurant).all()
    all_data = []
    for restaurant in restaurants_list:
        menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
        restaurant_dict = {
            'restaurant_id':restaurant.id,
            'restaurant_name':restaurant.name,
            'restaurant_menu':[item.serialize for item in menu_items]
        }
        all_data.append(restaurant_dict)

    return jsonify({'restaurant_menus':all_data})


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
