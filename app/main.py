from flask import jsonify, request, Blueprint
from app import db

main = Blueprint('main', __name__)

# Connect to MongoDB
products_collection = db['products']  # Access the "products" collection

@main.route('/')
def home():
    return 'Welcome to the Store API! Now working with Flask+MongoDB!'

# manage products (add or get all products)
@main.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'GET':
        products = list(products_collection.find({}))
        for product in products:
            product["_id"] = str(product["_id"])  # Convert ObjectId to string
        return jsonify(products), 200

        #products = list(products_collection.find({}, {'_id': 0}))  # Exclude the '_id' field from results
        # return jsonify(products)
    elif request.method == 'POST':
        data = request.json # Get the JSON payload
        products_collection.insert_one(data) # Insert the data into the collection
        return jsonify({'message': 'Product added successfully!'}), 201

@main.route('/products/<name>', methods=['PUT'])
def update_product(name):
    if request.method == 'PUT':
        data = request.json
        result = products_collection.update_one({'name': name}, {'$set': data})
        if result.matched_count > 0:
            return jsonify({'message': 'Product updated successfully!'}), 200
        return jsonify({'message': 'Product not found!'}), 404
    elif request.method == 'DELETE':
        result = products_collection.delete_one({'name': name})
        if result.deleted_count > 0:
            return jsonify({'message': 'Product deleted successfully!'}), 200
        return jsonify({'message': 'Product not found!'}), 404

@main.route('/api/products/under/<float:price>', methods=['GET'])
def get_products_under(price):
    products = list(products_collection.find({'price': {'$lt': price}}, {'_id': 0}))
    return jsonify(products)

