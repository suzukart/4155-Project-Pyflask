import os

from flask import Flask
from flask.cli import load_dotenv
from flask_pymongo import PyMongo, MongoClient
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
from bson.objectid import ObjectId

current_directory_name = os.path.dirname(os.path.abspath('database_creation.py'))
parent_directory_name = os.path.join(current_directory_name,'..')
load_dotenv(f"{parent_directory_name}/.env")

# Initialize extensions without binding to an app yet.

mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

uri = os.environ.get('URI')
client = MongoClient(uri)
db = client.get_database('textbookstore')
users = db.get_collection('users')
books = db.get_collection('Books')

def create_app():
    app = Flask(__name__)
    app.config['MONGO_URI'] = uri
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
  

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

    # Register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/api')
    from app.profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint, url_prefix='/api/profile')

    return app
