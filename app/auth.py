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
        'password': hashed,
        'sessions': []
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
            'username': current_user.username,
            'sessions': current_user.sessions
        },
        'redirect': '/'
    }), 201

@auth.route('/login', methods=['POST', 'GET'])
def login():
    data = request.get_json() # get JSON payload
    email = data['email']
    password = data['password']
    print(password)
    user_info = users.find_one(
        {'email': email}
    )
    if user_info is not None:
        if bcrypt.check_password_hash(user_info['password'], password):
            user = Profile(user_info)
            login_user(user, remember=True)
            cookie_handler(user_info)

            return jsonify({
                'message': 'Success!',
                'user': {
                    '_id': str(user_info['_id']),
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

    else:
        return jsonify({
            'error': 'No account found with that email! Please sign up instead.',
            'redirect': '/signup'
        }), 404

@auth.route('/logout')
@login_required
def logout():
    session.permanent = False
    sid = session.get('sid')

    if sid:
        users.update_one({'_id': current_user.db_id},
                         {'$pull': {'sessions': sid}})

    session.clear()
    logout_user()

    return jsonify({
        'message': 'Logged out successfully'
    }), 200
