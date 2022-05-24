# -*- coding: utf-8 -*-
"""
Created on Fri May 20 13:46:00 2022

@author: luwes
"""

from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
from bson.json_util import loads, dumps
from flask import make_response
import database as db
import authentication
import logging
import ordermanagement as om


app = Flask(__name__)

# Set the secret key to some random bytes. 
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'


logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))

    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/loginError', methods=['GET', 'POST'])
def loginError():
    return render_template('loginError.html')

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        return redirect('/loginError')

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')


@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a 
    # quantity of 1 for now

    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]
    item["code"] = int(code)

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecart', methods = ['POST'])
def updatecart():
    # get cart dictionary from session memory
    cart = session["cart"]

    code = request.form.get('code')
    product = db.get_product(int(code))
    qty = request.form.get('quantity')
    qty = int(qty)

    ...
    
    cart[code]["qty"] = qty
    cart [code]["subtotal"] = qty * product["price"]

    ...
    # don't forget this
    session["cart"] = cart

    return redirect('/cart')

@app.route('/deleteitem')
def deleteitem():
    code = request.args.get('code', '')
    cart = session["cart"]
    cart.pop(code)
    session["cart"]=cart
    if(session.get("cart") == {}):
        for key in list(session["cart"].keys()):
            session["cart"].pop(key)
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/orders')
def orders():
    user = session["user"] 
    username = user["username"]
    order_list = db.get_orders(username)
    return render_template('orders.html', page="Orders", order_list=order_list)

@app.route('/changepass')
def changepass():
    return render_template('changepass.html')

@app.route('/authchange', methods = ['POST'])
def authchange():
    user = session["user"] 
    username = user["username"]
    user = db.get_user(username)
    oldpass = request.form.get('oldpass')
    newpass = request.form.get('newpass')
    check = request.form.get('re-enter')
    
    if(oldpass == user["password"] and newpass == check):
        db.update_user(username, newpass)
        return render_template('changesuccessful.html')
    
    return render_template('changefail.html')

@app.route('/api/products',methods=['GET'])
def api_get_products():
    resp = make_response( dumps(db.get_products()) )
    resp.mimetype = 'application/json'
    return resp

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_product(code):
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp
