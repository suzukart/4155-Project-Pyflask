from flask import Blueprint, request, jsonify
from app import bcrypt, users, active_sessions
from app.models import Profile
from flask_login import current_user, login_required, login_user, logout_user

profile = Blueprint('profile', __name__)

@profile.route('/users/<username>')
def user_profile(username):
    user = Profile.query.filter_by(username=username).first()
    if user:
        return jsonify({
            'id': user.get_id(),
            'email': user.email,
            'username': user.username
        }), 200
    else:
        return jsonify({
            'error': 'User not found.'
        }), 404

@profile.route('/active_sessions')
def show_my_sessions():
    if current_user.is_authenticated:
        all_sessions = list(active_sessions.find({
            "user_id": current_user.db_id
        }))
        # Return them to the front-end for display
        return jsonify({'active_sessions': all_sessions})
    return jsonify({'error': 'Not logged in'}), 401

@profile.route('/remove_session', methods=['POST'])
def remove_session():
    if current_user.is_authenticated:
        data = request.get_json()
        device_id = data.get('device_id')
        if device_id:
            active_sessions.delete_one({
                'user_id': current_user.db_id,
                'device_id': device_id
            })
            return jsonify({'message': 'Session removed.',
                            'redirect': '/active_sessions'}), 200
        return jsonify({'error': 'No device_id provided.'}), 400
    return jsonify({'error': 'Not logged in'}), 401


