from flask import Blueprint, request, jsonify
import bcrypt
from app import bcrypt, users
from app.models import Profile
from flask_login import current_user, login_required, login_user, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['POST', 'GET'])
def signup():
    data = request.get_json()
    email = data['email']
    username = data['username']
    password = data['password']
    existing_user = users.find_one({
        'email': email
    })
    if existing_user is not None:
        return jsonify({
            'error': 'Account already exists with that email! '
                     'Try a different email or please log in instead.',
            'redirect': '/signup'
        }), 400

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user_info = {
        'email': email,
        'username': username,
        'password': hashed
    }
    users.insert_one(user_info)
    login_user(Profile(user_info))

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
    data = request.get_json() # get JSON payload
    email = data['email']
    password = data['password']
    user_info = users.find_one(
        {'email': email}
    )
    if user_info is not None:
        if bcrypt.check_password_hash(user_info['password'], password):
            user = Profile(user_info)
            login_user(user)
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
                'error': 'Invalid email or password! Please try again, '
                         'or if you meant to sign up, please sign up instead!.',
                'redirect': '/login'
            }), 404

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({
        'message': 'Logged out successfully'
    }), 200