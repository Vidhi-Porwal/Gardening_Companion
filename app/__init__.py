## init.py
from flask import Flask, current_app
from flask_login import LoginManager
import pymongo
import os
from bson import ObjectId
from dotenv import load_dotenv
from .models import User
# from flask_dance.contrib.google import make_google_blueprint
from urllib.parse import quote_plus
from flask_mail import Mail


# Load environment variables
load_dotenv()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login"
mail = Mail()  # Initialize mail here, but configure it inside create_app

@login_manager.user_loader
def load_user(user_id):
    db = current_app.config['DB_CONNECTION']
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(
            id=str(user['_id']),
            full_name=user['full_name'],
            username=user['username'],
            email=user['email'],
            phone_no=user.get('phone_no'),
            role=user.get('role', 'user')
        )
    return None
    
from dotenv import load_dotenv
load_dotenv()
def create_app():
    """
    Application Factory: Creates and configures the Flask app.
    """
    app = Flask(__name__)
    MONGO_USER = os.getenv("MONGO_USER")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
    MONGO_USER = quote_plus(MONGO_USER) if MONGO_USER else ""
    MONGO_PASSWORD = quote_plus(MONGO_PASSWORD) if MONGO_PASSWORD else ""
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")
    
    # Create the final MongoDB URI
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}?authSource={MONGO_AUTH_SOURCE}"


    # Load configurations
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'DEV')
    app.config['MONGO_URI'] = MONGO_URI
    app.config['MONGO_DB_NAME'] = os.getenv('MONGO_DB_NAME')


    # Email Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
    app.config['MAIL_PORT'] = 587  # Use port 587 for TLS
    app.config['MAIL_USE_TLS'] = True  
    app.config['MAIL_USE_SSL'] = False  # Don't use SSL since TLS is enabled
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')


    # Set up MongoDB connection
    try:
        mongo_client = pymongo.MongoClient(app.config['MONGO_URI'])
        db = mongo_client[app.config['MONGO_DB_NAME']]
        app.config['DB_CONNECTION'] = db
    except pymongo.errors.PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

    # Initialize Flask extensions
    login_manager.init_app(app)
    mail.init_app(app)  # Initialize Flask-Mail


    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    from .auth import auth, google_blueprint  # Import google_blueprint
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(google_blueprint, url_prefix='/login')  # Register OAuth Google Login


    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    from .profile import profile_bp
    app.register_blueprint(profile_bp, url_prefix="/profile")

    return app