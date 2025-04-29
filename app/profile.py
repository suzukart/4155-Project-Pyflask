from flask import Blueprint, request, jsonify
from app import bcrypt, users
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
            'username': user.username,
            'listing': user.listings,
            'profile_image': user.profile_image,
            'purchase_history': user.purchase_history,
        }), 200
    else:
        return jsonify({
            'error': 'User not found.'
        }), 404

