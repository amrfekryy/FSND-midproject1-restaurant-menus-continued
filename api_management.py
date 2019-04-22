# add database directory to python modules path.
import sys
sys.path.append("./database/")

# flask
from flask import (Blueprint, render_template, jsonify)
# general
from helpers import *
# database
from db_session import session, Restaurant, MenuItem


# create blueprint
# http://flask.pocoo.org/docs/1.0/blueprints/
api_management = Blueprint('api_management', __name__,
                     template_folder='templates', 
                     static_folder='static')


@api_management.route('/api/')
def api():
    return render_template('api.html')


@api_management.route('/api/restaurants/')
@login_required
def api_restaurants():
    restaurants_list = session.query(Restaurant).all()    
    return jsonify({'restaurants':[restaurant.serialize for restaurant in restaurants_list]})


@api_management.route('/api/restaurant/<int:restaurant_id>/')
@login_required
def api_restaurant(restaurant_id):
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    except:
        return f"There is no restaurant with id = {restaurant_id}"

    restaurant_dict = restaurant.serialize
    restaurant_dict['restaurant_menu'] = [item.serialize for item in restaurant.menu_items]
    return jsonify(restaurant_dict)


@api_management.route('/api/menu_item/<int:item_id>/')
@login_required
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


@api_management.route('/api/all/')
@login_required
def api_all():
    restaurants_list = session.query(Restaurant).all()
    all_data = []
    for restaurant in restaurants_list:
        restaurant_dict = restaurant.serialize
        restaurant_dict['restaurant_menu'] = [item.serialize for item in restaurant.menu_items]
        all_data.append(restaurant_dict)

    return jsonify({'restaurant_menus':all_data})
