from flask import jsonify, request, Blueprint
from app import db, bcrypt
from bson import ObjectId
import gridfs
import datetime

main = Blueprint('main', __name__)

# Connect to MongoDB
products_collection = db['products']  # Access the "products" collection
listings_collection = db['Listings']  # Access the "Listings" collection
books_collection = db['Books'] # Access the "Books" collection
users_collection = db['Users'] # Access the "Users" collection

fs = gridfs.GridFS(db) # Establish the gridfs to upload images

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
# http://localhost:5000/apidocs/
#################################
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
    """
    Add a new listing with image
    ---
    tags:
      - Listings
    consumes:
      - multipart/form-data
    parameters:
      - name: Image
        in: formData
        type: file
        required: true
      - name: Price
        in: formData
        type: string
        required: true
      - name: City
        in: formData
        type: string
        required: true
      - name: Category
        in: formData
        type: string
        required: true
    responses:
      201:
        description: Listing added successfully
      400:
        description: Missing required fields
    """
    if 'Image' not in request.files:
        return jsonify({'message': 'Image file is required'}), 400

    image_file = request.files['Image']
    other_fields = request.form  # Get remaining fields from form-data

    required_fields = ('Price', 'City', 'Category')
    if not all(key in other_fields for key in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    image_id = fs.put(image_file, filename=image_file.filename)

    listing_data = {
        'Image': str(image_id),
        'Price': other_fields['Price'],
        'City': other_fields['City'],
        'Category': other_fields['Category']
    }

    listings_collection.insert_one(listing_data)
    return jsonify({'message': 'Listing added successfully!'}), 201

# Fetch all Listings
@main.route('/listings', methods=['GET'])
def get_listings():
    """
    Get all listings
    ---
    tags:
      - Listings
    responses:
      200:
        description: A list of all listings
    """
    listings = list(listings_collection.find({}))
    for listing in listings:
        listing['_id'] = str(listing['_id'])
    return jsonify(listings), 200

@main.route('/listings/<string:id>', methods=['GET'])
def get_listing_by_id(id):
    """
    Get listing by ID
    ---
    tags:
      - Listings
    parameters:
      - name: id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Listing found
      400:
        description: Invalid ID format
      404:
        description: Listing not found
    """
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
    """
    Update a listing by ID
    ---
    tags:
      - Listings
    consumes:
      - multipart/form-data
    parameters:
      - name: id
        in: path
        required: true
        type: string
      - name: Image
        in: formData
        type: file
        required: false
      - name: Price
        in: formData
        type: string
        required: false
      - name: City
        in: formData
        type: string
        required: false
      - name: Category
        in: formData
        type: string
        required: false
    responses:
      200:
        description: Listing updated successfully
      400:
        description: Invalid ID or no data to update
      404:
        description: Listing not found
    """
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    update_fields = {}

    if 'Image' in request.files:
        image_file = request.files['Image']
        image_id = fs.put(image_file, filename=image_file.filename)
        update_fields['Image'] = str(image_id)

    for field in ('Price', 'City', 'Category'):
        if field in request.form:
            update_fields[field] = request.form[field]

    if not update_fields:
        return jsonify({'message': 'No data to update'}), 400

    result = listings_collection.update_one({'_id': ObjectId(id)}, {'$set': update_fields})

    if result.matched_count > 0:
        return jsonify({'message': 'Listing updated successfully!'}), 200
    return jsonify({'message': 'Listing not found!'}), 404

    if result.matched_count > 0:
        return jsonify({'message': 'Listing updated successfully!'}), 200
    return jsonify({'message': 'Listing not found!'}), 404

# Delete a Listing
@main.route('/listings/<string:id>', methods=['DELETE'])
def delete_listing(id):
    """
    Delete a listing by ID
    ---
    tags:
      - Listings
    parameters:
      - name: id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Listing deleted successfully
      400:
        description: Invalid ID format
      404:
        description: Listing not found
    """
    if not ObjectId.is_valid(id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    result = listings_collection.delete_one({'_id': ObjectId(id)})

    if result.deleted_count > 0:
        return jsonify({'message': 'Listing deleted successfully!'}), 200
    return jsonify({'message': 'Listing not found!'}), 404

@main.route('/listings/under/<float:price>', methods=['GET'])
def get_listings_under(price):
    """
    Get listings under a given price
    ---
    tags:
      - Listings
    parameters:
      - name: price
        in: path
        required: true
        type: number
    responses:
      200:
        description: Listings under the given price
    """
    listings = list(listings_collection.find({'Price': {'$lt': price}}, {'_id': 0}))
    return jsonify(listings)

# Get Listings by Category
@main.route('/listings/category/<category>', methods=['GET'])
def get_listings_by_category(category):
    """
    Get listings by category
    ---
    tags:
      - Listings
    parameters:
      - name: category
        in: path
        required: true
        type: string
    responses:
      200:
        description: Listings matching the category
    """
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
    """
    Add a new book
    ---
    tags:
      - Books
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - item
              - itemLabel
              - linkTo
              - mainSubject
              - mainSubjectLabel
            properties:
              item: { type: string }
              itemLabel: { type: string }
              linkTo: { type: string }
              mainSubject: { type: string }
              mainSubjectLabel: { type: string }
              _id: { type: string, example: "optional ObjectId string" }
    responses:
      201:
        description: Book added successfully
      400:
        description: Invalid input
    """
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
    """
    Get all books
    ---
    tags:
      - Books
    responses:
      200:
        description: List of books
    """
    books = list(books_collection.find({}))
    for book in books:
        book['_id'] = str(book['_id'])
    return jsonify(books), 200

# Fetch a Book by ID
@main.route('/books/<string:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    """
    Get a book by ID
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Book found
      404:
        description: Book not found
      400:
        description: Invalid ID format
    """
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
    """
    Update a book by ID
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        required: true
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
    responses:
      200:
        description: Book updated successfully
      404:
        description: Book not found
      400:
        description: Invalid ID format
    """
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
    """
    Delete a book by ID
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Book deleted successfully
      404:
        description: Book not found
      400:
        description: Invalid ID format
    """
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
    """
    Add a new user
    ---
    tags:
      - Users
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            example:
              name: John Doe
              email: john@example.com
              _id: optional ObjectId string
    responses:
      201:
        description: User added successfully
      400:
        description: Invalid ID format
    """
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
    """
    Get all users
    ---
    tags:
      - Users
    responses:
      200:
        description: List of users
    """
    users = list(users_collection.find({}))
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users), 200

# Fetch a User by ID
@main.route('/users/<string:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """
    Get a user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: User found
      404:
        description: User not found
      400:
        description: Invalid ID format
    """
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
    """
    Update a user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
    responses:
      200:
        description: User updated successfully
      404:
        description: User not found
      400:
        description: Invalid ID format
    """
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
    """
    Delete a user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: User deleted successfully
      404:
        description: User not found
      400:
        description: Invalid ID format
    """
    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid ID format!'}), 400

    result = users_collection.delete_one({'_id': ObjectId(user_id)})
    if result.deleted_count > 0:
        return jsonify({'message': 'User deleted successfully!'}), 200
    return jsonify({'message': 'User not found!'}), 404

@main.route('/users/password/<string:user_id>', methods=['PUT'])
def update_password(user_id):
    """
    Update a user's password.

    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        description: ID of the user to update
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - new_password
            properties:
              new_password:
                type: string
                minLength: 6
                description: New password for the user
    responses:
      200:
        description: Password updated successfully
      400:
        description: Invalid user ID or password format
      404:
        description: User not found
    """
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
    """
    Update a user's email address.

    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        description: ID of the user to update
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - new_email
            properties:
              new_email:
                type: string
                format: email
                description: New email address for the user
    responses:
      200:
        description: Email updated successfully
      400:
        description: Invalid user ID or email format
      404:
        description: User not found
      409:
        description: Email already in use
    """
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
    """
    Upload and update a user's profile picture.

    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        description: ID of the user to update
        schema:
          type: string
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            required:
              - profile_picture
            properties:
              profile_picture:
                type: string
                format: binary
                description: Profile picture file to upload
    responses:
      200:
        description: Profile picture updated successfully
      400:
        description: Missing or invalid input
    """
    if 'profile_picture' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['profile_picture']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid user ID'}), 400

    # Store the user_id with the file as metadata
    metadata = {
        'user_id': user_id,
        'upload_date': datetime.datetime.now(),
        'content_type': file.content_type
    }

    file_id = fs.put(file,
                     filename=file.filename,
                     metadata=metadata)

    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'profile_picture': str(file_id)}}
    )

    return jsonify({'message': 'Profile picture updated!', 'file_id': str(file_id)}), 200


@main.route('/users/username/<string:user_id>', methods=['PUT'])
def update_username(user_id):
    """
    Update a user's username.

    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        description: ID of the user to update
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - new_username
            properties:
              new_username:
                type: string
                description: New username to set
    responses:
      200:
        description: Username updated successfully
      400:
        description: Invalid input or missing data
      404:
        description: User not found
      409:
        description: Username already taken
    """
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

# Helper route to get a user's profile image directly
@main.route('/users/<string:user_id>/profile-image', methods=['GET'])
def get_profile_image(user_id):
    """
    Retrieve a user's profile image
    """
    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid user ID format'}), 400

    try:
        # Find the user and get their profile picture ID
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user or 'profile_picture' not in user:
            return jsonify({'error': 'No profile picture found for this user'}), 404

        # Get the profile picture ID
        file_id = user['profile_picture']

        # Redirect to the general image endpoint
        from flask import redirect, url_for
        return redirect(url_for('main.get_image', file_id=file_id))
    except Exception as e:
        return jsonify({'error': f'Error retrieving profile image: {str(e)}'}), 500


@main.route('/image/<string:file_id>', methods=['GET'])
def get_image(file_id):
    """
    Retrieve an image from GridFS by its file_id
    Returns the image data with appropriate content type
    """
    if not ObjectId.is_valid(file_id):
        return jsonify({'error': 'Invalid file ID format'}), 400

    try:
        # Check if file exists first
        if not fs.exists(ObjectId(file_id)):
            return jsonify({'error': 'Image not found'}), 404

        # Find the file by its ID
        file_data = fs.get(ObjectId(file_id))

        # Create a response with the file data
        from flask import Response
        return Response(
            file_data.read(),
            mimetype='image/jpeg',  # Default mime type
            headers={
                'Content-Disposition': f'inline; filename="{file_data.filename}"'
            }
        )
    except Exception as e:
        return jsonify({'error': f'Error retrieving image: {str(e)}'}), 500


@main.route('/image/<string:file_id>/metadata', methods=['GET'])
def get_image_metadata(file_id):
    """
    Retrieve metadata for an image from GridFS by its file_id
    """
    if not ObjectId.is_valid(file_id):
        return jsonify({'error': 'Invalid file ID format'}), 400

    try:
        # Get the file object without downloading the content
        file = db.fs.files.find_one({'_id': ObjectId(file_id)})

        if not file:
            return jsonify({'error': 'File not found'}), 404

        # Extract relevant metadata
        metadata = {
            'filename': file.get('filename'),
            'content_type': file.get('contentType', 'unknown'),
            'upload_date': file.get('uploadDate'),
            'length': file.get('length'),
        }

        # Add user metadata if exists
        if 'metadata' in file and file['metadata']:
            metadata.update(file['metadata'])

        return jsonify(metadata), 200
    except Exception as e:
        return jsonify({'error': f'Error retrieving metadata: {str(e)}'}), 500


# Find all images for a specific user
@main.route('/users/<string:user_id>/images', methods=['GET'])
def get_user_images(user_id):
    """
    Find all images that belong to a specific user
    """
    if not ObjectId.is_valid(user_id):
        return jsonify({'error': 'Invalid user ID format'}), 400

    try:
        # Query for files with matching user_id in metadata
        files = list(db.fs.files.find({'metadata.user_id': user_id}))

        if not files:
            return jsonify({'message': 'No images found for this user', 'images': []}), 200

        # Format the results
        images = []
        for file in files:
            images.append({
                'file_id': str(file['_id']),
                'filename': file.get('filename'),
                'upload_date': file.get('uploadDate'),
                'metadata': file.get('metadata', {})
            })

        return jsonify({'images': images}), 200
    except Exception as e:
        return jsonify({'error': f'Error retrieving user images: {str(e)}'}), 500