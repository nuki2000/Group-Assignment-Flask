# -*- coding: utf-8 -*-
"""
Created on Fri May 20 22:05:46 2022

@author: luwes
"""

import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

products_db = myclient["products"]
order_management_db = myclient["order_management"]

def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def update_user(username, newPass):
    order_management_db['customers'].update_one({"username":username}, {"$set":{"password":newPass}})
    return 

def get_product(code):
    products_coll = products_db["products"]

    product = products_coll.find_one({"code":code},{"_id":0})

    return product

def get_products():
    product_list = []

    products_coll = products_db["products"]

    for p in products_coll.find({},{"_id":0}):
        product_list.append(p)

    return product_list

def get_branch(code):
    branches_coll = products_db["branches"]

    branch = branches_coll.find_one({"code":str(code)})

    return branch

def get_branches():
    branch_list = []

    branches_coll = products_db["branches"]

    for b in branches_coll.find({}):
        branch_list.append(b)

    return branch_list

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert_one(order)

def get_orders(username):
    order_list = []
    order_coll = order_management_db["orders"]
    
    for o in order_coll.find({"username": username}):
        order_list.append(o)
        
    return order_list
