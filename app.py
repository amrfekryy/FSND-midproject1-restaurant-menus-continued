# add database directory to python modules path.
import sys
sys.path.append("./database/")

# flask
from flask import ( 
    Flask, render_template, request, redirect, 
    url_for, flash, jsonify )
# blueprints
from login_management import login_management
from api_management import api_management
# general
from helpers import *
from worldwide_mashup_helpers import *
# database
from db_session import session, Restaurant, MenuItem, User


# initialize flask app
app = Flask(__name__)
# register blueprints
app.register_blueprint(login_management)
app.register_blueprint(api_management)


# clear orm session after each request
@app.teardown_request
def remove_session(ex=None):
    session.remove()
# https://stackoverflow.com/a/34010159
# https://stackoverflow.com/q/30521112


@app.route('/')
@app.route('/restaurants/')
def index():

    restaurants_list = session.query(Restaurant).all()
    user = get_user(login_session.get('user_id')) 
    return render_template('index.html', restaurants_list=restaurants_list, user=user)


@app.route('/restaurants/add/', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    
    if request.method == 'POST':

        restaurant_name = request.form.get('restaurant_name')
        if restaurant_name:

            new_restaurant = Restaurant(
                name=restaurant_name,
                user_id=login_session['user_id'])
            session.add(new_restaurant)
            session.commit()
            flash(f"New restaurant \"{restaurant_name}\" has been added")
            return redirect(url_for('index'))
        else:
            return "Name field is empty!"
    
    else:
        user = get_user(login_session.get('user_id'))
        return render_template('add_restaurant.html', user=user)


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@login_required
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
        is_logged_in, is_owner = get_permissions(login_session.get('user_id'), restaurant)
        if not is_owner:
            return "You Are not the owner of this restaurant"
        else:
            user = get_user(login_session.get('user_id'))
            return render_template('edit_restaurant.html', restaurant=restaurant, user=user)


@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_restaurant(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    restaurant_name = restaurant.name

    if request.method == 'POST':

        answer = request.form.get('answer')
        if answer == 'yes':
            for item in restaurant.menu_items:
                session.delete(item)
            session.delete(restaurant)
            session.commit()
            flash(f"Restaurant \"{restaurant_name}\" has been deleted")
            return redirect(url_for('index'))
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    
    else:
        is_logged_in, is_owner = get_permissions(login_session.get('user_id'), restaurant)
        if not is_owner:
            return "You Are not the owner of this restaurant"
        else:
            user = get_user(login_session.get('user_id'))
            return render_template('delete_restaurant.html', restaurant=restaurant, user=user)


@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurant_menu(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    is_logged_in, is_owner = get_permissions(login_session.get('user_id'), restaurant)
    user = get_user(login_session.get('user_id'))

    return render_template('restaurant_menu.html', 
        restaurant=restaurant, menu_items=restaurant.menu_items, 
        user=user, is_owner=is_owner)


@app.route('/restaurants/<int:restaurant_id>/menu/add', methods=['GET', 'POST'])
@login_required
def add_menu_item(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if request.method == 'POST':

        item_name = request.form.get('item_name')
        item_price = request.form.get('item_price')
        item_description = request.form.get('item_description')
        item_course = request.form.get('item_course')
        if item_name and item_price and item_description and item_course:

            new_item = MenuItem(
                name=item_name, 
                price=item_price, 
                description=item_description, 
                course=item_course, 
                restaurant_id=restaurant_id,
                user_id=login_session['user_id'])
            session.add(new_item)
            session.commit()
            flash(f"New item \"{item_name}\" has been added")
            return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
        else:
            return "One or more fields is empty!"
    
    else:
        is_logged_in, is_owner = get_permissions(login_session.get('user_id'), restaurant)
        if not is_owner:
            return "You Are not the owner of this restaurant"
        else:
            user = get_user(login_session.get('user_id'))
            return render_template('add_menu_item.html', restaurant_id=restaurant_id, user=user)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
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
        is_logged_in, is_owner = get_permissions(login_session.get('user_id'), restaurant)
        if not is_owner:
            return "You Are not the owner of this restaurant"
        else:
            user = get_user(login_session.get('user_id'))
            return render_template('edit_menu_item.html', restaurant=restaurant, menu_item=menu_item, user=user)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
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
        is_logged_in, is_owner = get_permissions(login_session.get('user_id'), restaurant)
        if not is_owner:
            return "You Are not the owner of this restaurant"
        else:
            user = get_user(login_session.get('user_id'))
            return render_template('delete_menu_item.html', restaurant=restaurant, menu_item=menu_item, user=user)


@app.route('/worldwide/', methods=['GET', 'POST'])
@login_required
def worldwide_mashup():
    if request.method == 'POST':
        # get and verify form inputs
        address = request.form.get('address')
        try: radius = int(request.form.get('radius'))
        except: return "Range of search must be an integer"
        meal = request.form.get('meal')

        if not (address and radius and meal):
            return "One or more search paramters is missing"
        
        # find restaurants via HERE, FOURSQUARE mashup
        mashup_results = find_restaurant(address, radius, meal)
        if not mashup_results:
            return "No result was found"
        if mashup_results == "API error":
            return "Somethig went wrong, please try another address"            

        # display results on page
        # return jsonify(mashup_results)
        return render_template('worldwide_mashup.html', mashup_results=mashup_results)

    else:
        user = get_user(login_session.get('user_id'))
        return render_template('worldwide_mashup.html', user=user)


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
