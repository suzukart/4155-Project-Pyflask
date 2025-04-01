from flask import Blueprint, request, jsonify, session, current_app
import uuid
from flask_login import login_user, current_user
from app import bcrypt, users
from app.models import Profile

auth = Blueprint('auth', __name__)

def cookie_handler(user_info):
    # Generate a session identifier and store it in Flask's session.
    sid = str(uuid.uuid4())
    session['sid'] = sid

@auth.route('/signup', methods=['POST', 'GET'])
def signup():
    data = request.get_json()
    email = data['email']
    username = data['username']
    password = data['password']
    existing_user = users.find_one({'email': email})
    if existing_user is not None:
        return jsonify({
            'error': 'Account already exists with that email! Try a different email or log in instead.',
            'redirect': '/signup'
        }), 400

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user_info = {
        'email': email,
        'username': username,
        'password': hashed
    }
    result = users.insert_one(user_info)
    user_info['_id'] = result.inserted_id
    login_user(Profile(user_info))
    cookie_handler(user_info)

    return jsonify({
        'message': 'Account created and successfully logged in!',
        'user': {
            'id': current_user.get_id(),
            'email': current_user.email,
            'username': current_user.username
        },
        'redirect': '/'
    }), 201

@auth.route('/login', methods=['POST', 'GET'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user_info = users.find_one({'email': email})
    if user_info:
        if bcrypt.check_password_hash(user_info['password'], password):
            user = Profile(user_info)
            login_user(user)
            cookie_handler(user_info)

            return jsonify({
                'message': 'Success!',
                'user': {
                    'id': user.get_id(),
                    'email': user.email,
                    'username': user.username
                },
                'redirect': '/'
            }), 200
        else:
            return jsonify({
                'error': 'Invalid email or password! Please try again.',
                'redirect': '/login'
            }), 404
    else:
        return jsonify({
            'error': 'No account found with that email! Please sign up instead.',
            'redirect': '/signup'
        }), 404

@auth.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    session.clear()
    return jsonify({
        'message': 'Logged out successfully'
    }), 200