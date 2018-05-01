# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 11:00:12 2018

@author: kiranvm
"""

from flask import Flask,render_template,request,redirect,url_for,jsonify,flash
from database_setup import Base,Restaurant,MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#New imports for session token generation
import random,string #for the random id generation
from flask import session as login_session

app = Flask(__name__)

#here comes the persistence layer
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#Fake Restaurants
#restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

#restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
#items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
#item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

#Create a state token to prevent request forgery
#store it in the session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return "The current session state is %s" %login_session['state']

#Here comes the JSON End points functions
@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant)
    ls = []
    for restaurant in restaurants:
        ls.append(restaurant.serialize)
    return jsonify(Restaurant=ls)

@app.route('/restaurants/<int:restaurant_id>/JSON')
def menuItemsJSON(restaurant_id):
    menuItems = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    ls = []
    for item in menuItems:
        ls.append(item.serialize)
    return jsonify(MenuItem=ls)

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(restaurant_id=restaurant_id,id=menu_id).one()
    return jsonify(MenuItem=menuItem.serialize)


#Here comes the restaurant routes & functions
@app.route('/')    
@app.route('/restaurants')
def showRestaurants():
    restaurants = session.query(Restaurant) #fetches all those wacky restaurants from the db
    return render_template('restaurants.html',restaurants=restaurants)

@app.route('/restaurants/new',methods=['GET','POST'])
def newRestaurant():
    if (request.method=='POST'):
        restaurant_id = random.randint(0, 9999) #see how to retrieve id of the just commited row using sqlalchemy to remove this line
        newRestaurant = Restaurant(name = request.form['name'],id=restaurant_id)
        session.add(newRestaurant)
        session.commit()
        #flash a message here about the item inserted
        flash("New restaurant created !")
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))
    else:
        return render_template('newrestaurant.html')
    
@app.route('/restaurants/<int:restaurant_id>/edit',methods=['GET','POST'])
def editRestaurant(restaurant_id):
    editRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()    
    if(request.method=='POST'):
        editRestaurant.name = request.form['name']
        session.add(editRestaurant)
        session.commit()
        #flash a message here about the item edited
        flash("Successfully edited the restaurant!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editrestaurant.html',restaurant=editRestaurant )

@app.route('/restaurants/<int:restaurant_id>/delete',methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    delRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()    
    if(request.method=='POST'):
        session.delete(delRestaurant )
        session.commit()
        #flash a message here about the item deleted
        flash("Successfully deleted the restaurant!")
        return redirect(url_for('showRestaurants'))        
    else:
        return render_template('deleterestaurant.html',restaurant=delRestaurant )


#Here comes the menu routes & functions
@app.route('/restaurants/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one() 
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id) #fetches all those lickalicious menu items of the restaurant
    return render_template('menu.html',restaurant=restaurant,items=items)

@app.route('/restaurants/<int:restaurant_id>/menu/new',methods=['GET','POST'])
def newMenu(restaurant_id):
    if (request.method == 'POST'):
        newItem = MenuItem(restaurant_id=restaurant_id,name=request.form['name'],description=request.form['description'],course=request.form['course'],price=request.form['price'])    
        session.add(newItem)
        session.commit()
        flash("New menu item created successfully!")
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one() 
        return render_template('newmenuitem.html',restaurant=restaurant)
    
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit',methods=['GET','POST'])
def editMenu(restaurant_id,menu_id):
    editItem = session.query(MenuItem).filter_by(id=menu_id,restaurant_id=restaurant_id).one()
    editRest = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if (request.method == 'POST'):
        editItem = session.query(MenuItem).filter_by(id=menu_id,restaurant_id=restaurant_id).one()
        if (request.form['name'] != ''):
            editItem.name = request.form['name'] 
        elif (request.form['description'] != ''):
            editItem.description = request.form['description'] 
        elif (request.form['course'] != ''):
            editItem.course = request.form['course']
        elif (request.form['price'] != ''):
            editItem.price = request.form['price']
            
        session.add(editItem)
        session.commit()
        flash("Menu item edited successfully !")
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html',restaurant=editRest,item=editItem)

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete',methods=['GET','POST'])
def deleteMenu(restaurant_id,menu_id):
    deleteItem = session.query(MenuItem).filter_by(id=menu_id,restaurant_id=restaurant_id).one()
    editRest = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if (request.method == 'POST'):
        session.delete(deleteItem)
        session.commit()
        flash("Menu item deleted successfully!")
        return redirect(url_for('showMenu',restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html',restaurant=editRest,item=deleteItem)


if __name__=='__main__':
    app.debug=True
    app.secret_key = 'super_secret_key'
    app.run(host = '0.0.0.0', port=5000)