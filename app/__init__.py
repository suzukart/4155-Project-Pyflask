import os
import uuid
from flask import Flask, request, session, jsonify, after_this_request
from flask.cli import load_dotenv
from flask_pymongo import PyMongo, MongoClient
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, logout_user
from flask_cors import CORS
from bson import ObjectId

current_directory_name = os.path.dirname(os.path.abspath('database_creation.py'))
parent_directory_name = os.path.join(current_directory_name,'..')
load_dotenv(f"{parent_directory_name}/.env")

# Initialize extensions without binding to an app yet.

mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

uri = os.getenv('URI')
client = MongoClient(uri)
db = client.get_database('textbookstore')
users = db.get_collection('users')
books = db.get_collection('Books')
active_sessions = db.get_collection('active_sessions')

def create_app():
    app = Flask(__name__)
    app.config['MONGO_URI'] = uri
    app.config['SECRET_KEY'] = os.getenv('secret_key')

    # Initialize extensions with the app.
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Enable CORS (uncomment for production)
    #CORS(app, resources={r'/api/*': {
    #    'origins': 'https://textbook-sharing-application.vercel.app'}
    #})

    # Development CORS enabled
    #TODO: REMOVE THIS BEFORE DEPLOYMENT
    CORS(app)

    # User loader function for Flask-Login
    from app.models import Profile
    @login_manager.user_loader
    def load_user(user_id):
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            return None
        return Profile(user_data)

    @app.before_request
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

    # Register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/api')
    from app.profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint, url_prefix='/api/profile')

    return app
