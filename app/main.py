from flask import jsonify, request, Blueprint
from app import db, bcrypt
from bson import ObjectId

main = Blueprint('main', __name__)

# Connect to MongoDB
products_collection = db['products']  # Access the "products" collection
listings_collection = db['Listings']  # Access the "Listings" collection
books_collection = db['Books'] # Access the "Books" collection
users_collection = db['Users'] # Access the "Users" collection

@main.route('/')
def home():
    return 'Welcome to the Store API! Now working with Flask+MongoDB!'

#################################################################################################
            # |  _ \  _ __  ___    __| | _   _   ___ | |_
            # | |_) || '__|/ _ \  / _` || | | | / __|| __|
            # |  __/ | |  | (_) || (_| || |_| || (__ | |_
            # |_|    |_|   \___/  \__,_| \__,_| \___| \__|
            #  _____             _                _         _
            # | ____| _ __    __| | _ __    ___  (_) _ __  | |_  ___
            # |  _|  | '_ \  / _` || '_ \  / _ \ | || '_ \ | __|/ __|
            # | |___ | | | || (_| || |_) || (_) || || | | || |_ \__ \
            # |_____||_| |_| \__,_|| .__/  \___/ |_||_| |_| \__||___/
            #                      |_|
#################################################################################################
#Some endpoints created with the help of ChatGPT
###############################################
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
            # | |    (_) ___ | |_ (_) _ __    __ _
            # | |    | |/ __|| __|| || '_ \  / _` |
            # | |___ | |\__ \| |_ | || | | || (_| |
            # |_____||_||___/ \__||_||_| |_| \__, |
            #                                |___/
            #  _____             _                _         _
            # | ____| _ __    __| | _ __    ___  (_) _ __  | |_  ___
            # |  _|  | '_ \  / _` || '_ \  / _ \ | || '_ \ | __|/ __|
            # | |___ | | | || (_| || |_) || (_) || || | | || |_ \__ \
            # |_____||_| |_| \__,_|| .__/  \___/ |_||_| |_| \__||___/
            #                      |_|
################################################################################################

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

@main.route('/listings/<string:id>', methods=['GET'])
def get_listing_by_id(id):
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID format!'}), 400
    try:
        listing = listings_collection.find_one({'_id': ObjectId(id)})
        if listing:
            listing['_id'] = str(listing['_id'])
            return jsonify(listing), 200
        return jsonify({'message': 'Listing not found!'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Update a Listing
@main.route('/listings/<string:id>', methods=['PUT'])
def update_listing(id):
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    data = request.json
    result = listings_collection.update_one({'_id': ObjectId(id)}, {'$set': data})

    if result.matched_count > 0:
        return jsonify({'message': 'Listing updated successfully!'}), 200
    return jsonify({'message': 'Listing not found!'}), 404

# Delete a Listing
@main.route('/listings/<string:id>', methods=['DELETE'])
def delete_listing(id):
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    result = listings_collection.delete_one({'_id': ObjectId(id)})

    if result.deleted_count > 0:
        return jsonify({'message': 'Listing deleted successfully!'}), 200
    return jsonify({'message': 'Listing not found!'}), 404

@main.route('/listings/under/<float:price>', methods=['GET'])
def get_listings_under(price):
    listings = list(listings_collection.find({'Price': {'$lt': price}}, {'_id': 0}))
    return jsonify(listings)

# Get Listings by Category
@main.route('/listings/category/<category>', methods=['GET'])
def get_listings_by_category(category):
    listings = list(listings_collection.find({'Category': category}, {'_id': 0}))
    return jsonify(listings), 200

#################################################################################################
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

# Add a new Book
@main.route('/books', methods=['POST'])
def add_book():
    data = request.json
    if not all(key in data for key in ('item', 'itemLabel', 'linkTo', 'mainSubject', 'mainSubjectLabel')):
        return jsonify({'message': 'Missing required fields'}), 400

    # Convert _id to ObjectId if provided
    if '_id' in data:
        if not ObjectId.is_valid(data['_id']):
            return jsonify({'error': 'Invalid ID format!'}), 400
        data['_id'] = ObjectId(data['_id'])

    books_collection.insert_one(data)
    return jsonify({'message': 'Book added successfully!'}), 201

# Fetch all Books
@main.route('/books', methods=['GET'])
def get_books():
    books = list(books_collection.find({}))
    for book in books:
        book['_id'] = str(book['_id'])
    return jsonify(books), 200

# Fetch a Book by ID
@main.route('/books/<string:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    if not ObjectId.is_valid(book_id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    book = books_collection.find_one({'_id': ObjectId(book_id)})
    if book:
        book['_id'] = str(book['_id'])
        return jsonify(book), 200
    return jsonify({'message': 'Book not found!'}), 404

# Update a Book
@main.route('/books/<string:book_id>', methods=['PUT'])
def update_book(book_id):
    if not ObjectId.is_valid(book_id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    data = request.json
    result = books_collection.update_one({'_id': ObjectId(book_id)}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({'message': 'Book updated successfully!'}), 200
    return jsonify({'message': 'Book not found!'}), 404

# Delete a Book
@main.route('/books/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    if not ObjectId.is_valid(book_id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    result = books_collection.delete_one({'_id': ObjectId(book_id)})
    if result.deleted_count > 0:
        return jsonify({'message': 'Book deleted successfully!'}), 200
    return jsonify({'message': 'Book not found!'}), 404

#################################################################################################
            # | | | | ___   ___  _ __
            # | | | |/ __| / _ \| '__|
            # | |_| |\__ \|  __/| |
            #  \___/ |___/ \___||_|
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
    #   Verify User endpoint are complete

# Add a new User
@main.route('/users', methods=['POST'])
def add_user():
    data = request.json

    # Convert _id to ObjectId if provided
    if '_id' in data:
        if not ObjectId.is_valid(data['_id']):
            return jsonify({'error': 'Invalid ID format!'}), 400
        data['_id'] = ObjectId(data['_id'])

    users_collection.insert_one(data)
    return jsonify({'message': 'User added successfully!'}), 201

# Fetch all Users
@main.route('/users', methods=['GET'])
def get_users():
    users = list(users_collection.find({}))
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users), 200

# Fetch a User by ID
@main.route('/users/<string:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user:
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    return jsonify({'message': 'User not found!'}), 404

# Update a User
@main.route('/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    data = request.json
    result = users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({'message': 'User updated successfully!'}), 200
    return jsonify({'message': 'User not found!'}), 404


# Delete a User
@main.route('/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    result = users_collection.delete_one({'_id': ObjectId(user_id)})
    if result.deleted_count > 0:
        return jsonify({'message': 'User deleted successfully!'}), 200
    return jsonify({'message': 'User not found!'}), 404

@main.route('/users/password/<string:user_id>', methods=['PUT'])
def update_password(user_id):
    data = request.json
    new_password = data.get('new_password')

    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid user ID'}), 400

    if not new_password or len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')

    result = users_collection.update_one(
        {'_id': ObjectId(user_id)},
        #ONLY STORES THE HASHED VERSION OF THE PASSWORD OTHER THAN THE PASSWORD ITSELF, IF CHECKING PASSWORD VERIFY YOU ARE HASHING BEFORE STORING/COMPARING
        {'$set': {'password': hashed}}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'message': 'Password updated successfully!'}), 200

@main.route('/users/email/<string:user_id>', methods=['PUT'])
def update_email(user_id):
    data = request.json
    new_email = data.get('new_email')

    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid user ID'}), 400

    if not new_email or '@' not in new_email:
        return jsonify({'error': 'Invalid email address'}), 400

    if not new_email or '.' not in new_email:
        return jsonify({'error': 'Invalid email address'}), 400

    if users_collection.find_one({'email': new_email}):
        return jsonify({'error': 'Email already in use'}), 409

    result = users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'email': new_email}}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'message': 'Email updated successfully!'}), 200

@main.route('/users/profile-picture/<string:user_id>/', methods=['PUT'])
def update_profile_picture(user_id):
    data = request.json
    new_picture_url = data.get('profile_picture')

    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid user ID'}), 400

    if not new_picture_url or not new_picture_url.startswith('http'):
        return jsonify({'error': 'Invalid image URL'}), 400

    result = users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'profile_picture': new_picture_url}}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'message': 'Profile picture updated!'}), 200

@main.route('/users/username/<string:user_id>', methods=['PUT'])
def update_username(user_id):
    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    data = request.json
    new_username = data.get('new_username')

    if not new_username:
        return jsonify({'error': 'New username is required'}), 400

    # Check if username already exists
    if users_collection.find_one({'username': new_username}):
        return jsonify({'error': 'Username already taken'}), 409

    result = users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'username': new_username}}
    )

    if result.matched_count > 0:
        return jsonify({'message': 'Username updated successfully!'}), 200
    return jsonify({'error': 'User not found'}), 404