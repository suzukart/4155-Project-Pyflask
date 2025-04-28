from app import db, orders, bcrypt, users
from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_required
from datetime import datetime
from bson import ObjectId
from app.models import Listing
from app.models import Profile

cart = Blueprint('cart', __name__)

@cart.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    listing_id = data.get('listing_id')
    quantity = data.get('quantity', 1)
    user_id = current_user.get_id()
    orders.update_one(
        {'_id': ObjectId(user_id)},
        {'$addToSet': {'cart': {'listing_id': ObjectId(listing_id), 'quantity': quantity}}},
        upsert=True
    )
    return jsonify({'message': 'Item added to cart successfully!'}), 200

@cart.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.get_json()
    listing_id = data.get('listing_id')
    user_id = current_user.get_id()
    orders.update_one(
        {'_id': ObjectId(user_id)},
        {'$pull': {'cart': {'listing_id': ObjectId(listing_id)}}}
    )
    return jsonify({'message': 'Item removed from cart successfully!'}), 200

@cart.route('/get_cart', methods=['GET'])
@login_required
def get_cart():
    # Ensure the cart exists for the user
    if not orders.find_one({'_id': ObjectId(current_user.get_id())}):
        orders.insert_one({'_id': ObjectId(current_user.get_id()), 'cart': []})

    user_id = current_user.get_id()
    cart_items = orders.find_one({'_id': ObjectId(user_id)}, {'cart': 1})
    if not cart_items:
        return jsonify({'cart': []}), 200

    cart_listings = []
    for item in cart_items['cart']:
        listing = db.listings.find_one({'_id': item['listing_id']})
        if listing:
            cart_listings.append({
                'listing_id': str(listing['_id']),
                'title': listing['title'],
                'author': listing['author'],
                'price': listing['price'],
                'quantity': item['quantity']
            })

    # Return only the user's cart
    return jsonify({'cart': cart_listings}), 200

@cart.route('/checkout', methods=['POST'])
@login_required
def checkout():
    user_id = current_user.get_id()
    # Get the user's cart
    user_cart_data = orders.find_one({'_id': ObjectId(user_id)}, {'cart': 1})
    
    if not user_cart_data or not user_cart_data.get('cart'):
        return jsonify({'message': 'Cart is empty, cannot proceed with checkout.'}), 400
    
    cart_items = user_cart_data['cart']
    
    # Ensure the user's purchase_history array exists in their profile
    users.update_one(
        {'_id': ObjectId(user_id)},
        {'$setOnInsert': {'purchase_history': []}},
        upsert=True
    )
    # Append the entire cart to purchase_history
    users.update_one(
        {'_id': ObjectId(user_id)},
        {'$push': {'purchase_history': {'items': cart_items, 'purchased_at': datetime.now()}}}
    )
    
    # Clear the user's cart
    orders.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'cart': []}}
    )
    
    return jsonify({'message': 'Checkout successful. Purchase history updated.'}), 200

