
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.db_setup import Base, Restaurant, MenuItem

# connect to DB and DB tables
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
# establish 'session' connection for CRUD executions
session = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)


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



if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
