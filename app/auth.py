from flask import Blueprint, request, jsonify, session
import bcrypt, uuid
from app import bcrypt, users
from app.models import Profile
from flask_login import current_user, login_required, login_user, logout_user

auth = Blueprint('auth', __name__)

def cookie_handler(user_info):
    sid = str(uuid.uuid4())
    session['sid'] = sid

    device_cookie_name = "my_device_id"
    device_id = request.cookies.get(device_cookie_name)
    if not device_id:
        device_id = str(uuid.uuid4())

    session_obj = {
        'sid': sid,
        'device_id': device_id,
    }

    users.update_one({'_id': user_info['_id']},
                     {'$push': {'sessions': session_obj}})
    session.modified = True
    return device_id

@auth.route('/signup', methods=['POST', 'GET'])
def signup():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    existing_user = users.find_one({'email': email})
    if existing_user is not None:
        return jsonify({
            'error': 'Account already exists with that email! Try a different email or please log in instead.',
            'redirect': '/signup'
        }), 400

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user_info = {
        'email': email,
        'username': username,
        'password': hashed,
        'sessions': [],
        'remember_tokens': []  # initialize remember tokens field
    }
    result = users.insert_one(user_info)
    user_info['_id'] = result.inserted_id
    login_user(Profile(user_info))
    cookie_handler(user_info)  # sets session keys and updates sessions array

    response = jsonify({
        'message': 'Account created and successfully logged in!',
        'user': {
            'id': current_user.get_id(),
            'email': current_user.email,
            'username': current_user.username,
        },
        'redirect': '/'
    })
    # Set the device cookie if needed.
    device_cookie_name = "my_device_id"
    device_id = request.cookies.get(device_cookie_name)
    if not device_id:
        device_id = str(uuid.uuid4())
        response.set_cookie(device_cookie_name, device_id, httponly=True)
    return response, 201

@auth.route('/login', methods=['POST', 'GET'])
def login():
    data = request.get_json()  # get JSON payload
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)
    user_info = users.find_one({'email': email})
    if user_info is not None:
        if bcrypt.check_password_hash(user_info['password'], password):
            user = Profile(user_info)
            login_user(user, remember=remember)
            cookie_handler(user_info)

            response = jsonify({
                'message': 'Success!',
                'user': {
                    'id': user.get_id(),
                    'email': user.email,
                    'username': user.username,
                },
                'redirect': '/'
            })
            
            if remember:
                persistent_token = str(uuid.uuid4())
                users.update_one(
                    {'_id': user_info['_id']},
                    {'$push': {'remember_tokens': persistent_token}}
                )
                response.set_cookie("remember_token", persistent_token, max_age=30*24*60*60, httponly=True)
            
            device_cookie_name = "my_device_id"
            device_id = request.cookies.get(device_cookie_name)
            if not device_id:
                device_id = str(uuid.uuid4())
                response.set_cookie(device_cookie_name, device_id, httponly=True)
            
            return response, 200
        else:
            return jsonify({
                'error': 'Invalid email or password! Please try again, or if you meant to sign up, please sign up instead.',
                'redirect': '/login'
            }), 404
    else:
        return jsonify({
            'error': 'No account found with that email! Please sign up instead.',
            'redirect': '/signup'
        }), 404

@auth.route('/logout')
@login_required
def logout():
    sid = session.get('sid')
    if sid:
        users.update_one(
            {'_id': current_user.db_id},
            {'$pull': {'sessions': {'sid': sid}}}
        )
    remember_token = request.cookies.get("remember_token")
    if remember_token:
        users.update_one(
            {'_id': current_user.db_id},
            {'$pull': {'remember_tokens': remember_token}}
        )
    session.clear()
    logout_user()
    response = jsonify({'message': 'Logged out successfully'})
    response.set_cookie("remember_token", "", expires=0)
    return response, 200