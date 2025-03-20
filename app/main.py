from flask import jsonify, request, Blueprint
from app import db

main = Blueprint('main', __name__)

# Connect to MongoDB
products_collection = db['products']  # Access the "products" collection
listings_collection = db['Listings']  # Access the "Listings" collection
books_collection = db['Books'] # Access the "Books" collection


@main.route('/')
def home():
    return 'Welcome to the Store API! Now working with Flask+MongoDB!'

# - Product Endpoints -----------------------------------------------------------------------------------------

# Fetch all products
@main.route('/products', methods=['GET'])
def get_products():
    products = list(products_collection.find({}))
    for product in products:
        product["_id"] = str(product["_id"])  # Convert ObjectId to string
    return jsonify(products), 200

    #products = list(products_collection.find({}, {'_id': 0}))  # Exclude the '_id' field from results
    # return jsonify(products)

# Add a new product
@main.route('/products', methods=['POST'])
def add_product():
    data = request.json  # Get the JSON payload
    products_collection.insert_one(data)  # Insert the data into the collection
    return jsonify({'message': 'Product added successfully!'}), 201

@main.route('/products/<name>', methods=['PUT'])
def update_product(name):
    data = request.json
    result = products_collection.update_one({'name': name}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({'message': 'Product updated successfully!'})
    return jsonify({'message': 'Product not found!'}), 404

@main.route('/products/<name>', methods=['DELETE'])
def delete_product(name):
    result = products_collection.delete_one({'name': name})
    if result.deleted_count > 0:
        return jsonify({'message': 'Product deleted successfully!'})
    return jsonify({'message': 'Product not found!'}), 404

@main.route('/products/under/<float:price>', methods=['GET'])
def get_products_under(price):
    products = list(products_collection.find({'price': {'$lt': price}}, {'_id': 0}))
    return jsonify(products)



#################################################################################################
# Listing Endpoints


# Add a new Listing
@main.route('/listings', methods=['POST'])
def add_listing():
    data = request.json
    if not all(key in data for key in ('Image', 'Price', 'City', 'Category')):
        return jsonify({'message': 'Missing required fields'}), 400
    listings_collection.insert_one(data)
    return jsonify({'message': 'Listing added successfully!'}), 201

# Fetch all Listings
@main.route('/listings', methods=['GET'])
def get_listings():
    listings = list(listings_collection.find({}))
    for listing in listings:
        listing['_id'] = str(listing['_id'])
    return jsonify(listings), 200

# Update a Listing
@main.route('/listings/<name>', methods=['PUT'])
def update_listing(name):
    data = request.json
    result = listings_collection.update_one({'name': name}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({'message': 'Listing updated successfully!'}), 200
    return jsonify({'message': 'Listing not found!'}), 404

@main.route('/listings/<name>', methods=['DELETE'])
def delete_listing(name):
    result = listings_collection.delete_one({'name': name})
    if result.deleted_count > 0:
        return jsonify({'message': 'Product deleted successfully!'})
    return jsonify({'message': 'Product not found!'}), 404

@main.route('/listings/under/<float:price>', methods=['GET'])
def get_listings_under(price):
    listings = list(listings_collection.find({'price': {'$lt': price}}, {'_id': 0}))
    return jsonify(listings)

# Get Listings by Category
@main.route('/listings/category/<category>', methods=['GET'])
def get_listings_by_category(category):
    listings = list(listings_collection.find({'Category': category}, {'_id': 0}))
    return jsonify(listings), 200


#################################################################################################

            #  ____                 _
            # | __ )   ___    ___  | | __
            # |  _ \  / _ \  / _ \ | |/ /
            # | |_) || (_) || (_) ||   <
            # |____/  \___/  \___/ |_|\_\
            #  _____             _                _         _
            # | ____| _ __    __| | _ __    ___  (_) _ __  | |_  ___
            # |  _|  | '_ \  / _` || '_ \  / _ \ | || '_ \ | __|/ __|
            # | |___ | | | || (_| || |_) || (_) || || | | || |_ \__ \
            # |_____||_| |_| \__,_|| .__/  \___/ |_||_| |_| \__||___/
            #                      |_|

################################################################################################

    #    _  _   .___________.  ______    _______   ______
    #  _| || |_ |           | /  __  \  |       \ /  __  \
    # |_  __  _|`---|  |----`|  |  |  | |  .--.  |  |  |  |
    #  _| || |_     |  |     |  |  |  | |  |  |  |  |  |  |
    # |_  __  _|    |  |     |  `--'  | |  '--'  |  `--'  |
    #   |_||_|      |__|      \______/  |_______/ \______/


# Add a new Book
@main.route('/books', methods=['POST'])
def add_book():
    data = request.json
    if not all(key in data for key in ('item', 'itemLabel', 'linkTo', 'mainSubject', 'mainSubjectLabel')):
        return jsonify({'message': 'Missing required fields'}), 400
    books_collection.insert_one(data)
    return jsonify({'message': 'Book added successfully!'}), 201

# Fetch all Books
@main.route('/books', methods=['GET'])
def get_books():
    books = list(books_collection.find({}))
    for book in books:
        book['_id'] = str(book['_id'])
    return jsonify(books), 200

# Update a Book
@main.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    result = books_collection.update_one({'_id': book_id}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({'message': 'Book updated successfully!'}), 200
    return jsonify({'message': 'Book not found!'}), 404

# Delete a Book
@main.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    result = books_collection.delete_one({'_id': book_id})
    if result.deleted_count > 0:
        return jsonify({'message': 'Book deleted successfully!'}), 200
    return jsonify({'message': 'Book not found!'}), 404
