# add database directory to python modules path.
import sys
sys.path.append("./database/")

# flask
from flask import (Blueprint, render_template, request, jsonify)
# general
from helpers import *
# database
from db_session import session, Restaurant, MenuItem, User


# create blueprint
# http://flask.pocoo.org/docs/1.0/blueprints/
api_management = Blueprint('api_management', __name__,
                     template_folder='templates', 
                     static_folder='static')


# API documnetation
@api_management.route('/api/')
def api():
    user = get_user(login_session.get('user_id'))
    return render_template('api.html', user=user)


# GET all restaurants
@api_management.route('/api/restaurants/', methods=['GET', 'POST'])
def api_restaurants():
    if request.method == 'GET':
        restaurants_list = session.query(Restaurant).all()    
        return jsonify({'restaurants':[restaurant.serialize for restaurant in restaurants_list]})

    elif request.method == 'POST':

        restaurant_name = request.args.get('name')
        user_id = request.args.get('user_id')

        # check all parameters were provided
        if restaurant_name and user_id:
            # verify user id
            try:
                session.query(User).filter_by(id=user_id).one()
            except:
                return jsonify({
                    'success':False,
                    'description': f'There is no user with id:{user_id}' 
                    }), 400

            # add restaurant
            new_restaurant = Restaurant(
                name=restaurant_name,
                user_id=user_id)
            session.add(new_restaurant)
            session.commit()
            return jsonify({
                    'success':True,
                    'description': f'A new restaurant has been added by user with id:{user_id}' 
                    }), 200

        else:
            return jsonify({
                'success':False, 
                'description': "One or more parameters is missing"
                }), 400



# GET/ PUT/DELETE an existing restaurant, POST a new menu_item
@api_management.route('/api/restaurant/<int:restaurant_id>/', methods=['GET', 'PUT', 'DELETE', 'POST'])
def api_restaurant(restaurant_id):
    # verify id exists in database
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    except:
        return jsonify({
            'success':False, 
            'description': f'There is no restaurant with id:{restaurant_id}'
            }), 400

    if request.method == 'GET':
        restaurant_dict = restaurant.serialize
        restaurant_dict['restaurant_menu'] = [item.serialize for item in restaurant.menu_items]
        return jsonify(restaurant_dict)

    elif request.method == 'PUT':
        restaurant_new_name = request.args.get('name')

        if restaurant_new_name:
            restaurant.name = restaurant_new_name
            session.add(restaurant)
            session.commit()
            return jsonify({
                'success':True, 
                'description': f'Restaurant with id:{restaurant_id} has been updated'
                }), 200
        else:
            return jsonify({
                'success':False, 
                'description': "'name' parameter was not provided"
                }), 400

    elif request.method == 'DELETE':
        for item in restaurant.menu_items:
            session.delete(item)
        session.delete(restaurant)
        session.commit()
        return jsonify({
            'success':True, 
            'description': f'Restaurant with id:{restaurant_id} has been deleted'
            }), 200

    elif request.method == 'POST':
        item_name = request.args.get('name')
        item_price = request.args.get('price')
        item_description = request.args.get('description')
        item_course = request.args.get('course')        
        user_id = request.args.get('user_id')

        # check all parameters were provided
        if item_name and item_price and item_description and item_course and user_id:
            # verify user id
            try:
                session.query(User).filter_by(id=user_id).one()
            except:
                return jsonify({
                    'success':False,
                    'description': f'There is no user with id:{user_id}' 
                    }), 400
            # add the item
            new_item = MenuItem(
                name=item_name, 
                price=item_price, 
                description=item_description, 
                course=item_course, 
                restaurant_id=restaurant_id,
                user_id=user_id)
            session.add(new_item)
            session.commit()
            return jsonify({
                'success':True, 
                'description': f'A new item has been added to restaurant with id:{restaurant_id}'
                }), 200
        else:
            return jsonify({
                'success':False,
                'description': 'One or more parameters is missing' 
                }), 400



# GET/ PUT/DELETE an existing menu item
@api_management.route('/api/menu_item/<int:item_id>/', methods=['GET', 'PUT', 'DELETE'])
def api_menu_item(item_id):
    # verify id exists in database
    try:
        menu_item = session.query(MenuItem).filter_by(id=item_id).one()
    except:
        return jsonify({
            'success':False, 
            'description': f'There is no menu item with id:{item_id}'
            }), 400
    
    if request.method == 'GET':
        restaurant = menu_item.restaurant
        item_dict = {
            'restaurant_id':restaurant.id,
            'restaurant_name':restaurant.name,
            'menu_item':menu_item.serialize
        }
        return jsonify(item_dict)

    elif request.method == 'PUT':

        item_new_name = request.args.get('name')
        item_new_price = request.args.get('price')
        item_new_description = request.args.get('description')
        item_new_course = request.args.get('course')

        if not (item_new_name or item_new_price or item_new_description or item_new_course):
            return jsonify({
                'success':False, 
                'description': "No parameters were provided"
                }), 400
        
        if item_new_name: menu_item.name = item_new_name
        if item_new_price: menu_item.price = item_new_price
        if item_new_description: menu_item.description = item_new_description
        if item_new_course: menu_item.course = item_new_course
        
        session.add(menu_item)
        session.commit()
        return jsonify({
            'success':True, 
            'description': f'Item with id:{item_id} has been updated'
            }), 200

    elif request.method == 'DELETE':
        session.delete(menu_item)
        session.commit()
        return jsonify({
            'success':True, 
            'description': f'Item with id:{item_id} has been deleted'
            }), 200


# GET all data
@api_management.route('/api/all/')
def api_all():
    restaurants_list = session.query(Restaurant).all()
    all_data = []
    for restaurant in restaurants_list:
        restaurant_dict = restaurant.serialize
        restaurant_dict['restaurant_menu'] = [item.serialize for item in restaurant.menu_items]
        all_data.append(restaurant_dict)

    return jsonify({'restaurant_menus':all_data})
