from flask import Blueprint, request, jsonify, session, after_this_request
import bcrypt, uuid
from bson import ObjectId
from app import bcrypt, users, Session
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

    users.update_one({'_id': user_info['_id']},
                     {'$push': {
                         'sessions': sid,
                         'device_id': device_id
                     }})

@auth.before_request
def check_device_id():
    device_cookie_name = "my_device_id"
    device_id = request.cookies.get(device_cookie_name)

    if not device_id:
        device_id = str(uuid.uuid4())

        @after_this_request
        def set_device_cookie(response):
            response.set_cookie(device_cookie_name, device_id, httponly=True)
            return response

    # If the user is authenticated, do some check with device_id
    if current_user.is_authenticated and device_id:
        current_sid = session.get('sid')

        user_doc = users.find_one({"_id": ObjectId(current_user.get_id())})

        sessions = user_doc.get('sessions', [])
        matching_session = next(
            (s for s in sessions if s.get('sid') == current_sid),
            None
        )
        if not matching_session:
            logout_user()
            return jsonify({'error': 'Session expired. Please log in again.'}), 401

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
    users.insert_one(user_info)
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