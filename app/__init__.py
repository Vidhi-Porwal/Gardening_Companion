## init.py
from flask import Flask, current_app
from flask_login import LoginManager
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
import pymongo
import os
from bson import ObjectId
from urllib.parse import quote_plus
from dotenv import load_dotenv
from .models import User

# Load environment variables
load_dotenv()

# Initialize Flask extensions
login_manager = LoginManager()
login_manager.login_view = "auth.login"
mail = Mail()
oauth = OAuth()

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

def create_app():
    """
    Application Factory: Creates and configures the Flask app.
    """
    app = Flask(__name__)

    # MongoDB Configuration
    MONGO_USER = quote_plus(os.getenv("MONGO_USER", ""))
    MONGO_PASSWORD = quote_plus(os.getenv("MONGO_PASSWORD", ""))
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}?authSource={MONGO_AUTH_SOURCE}"

    # App Configurations
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'DEV')
    app.config['MONGO_URI'] = MONGO_URI
    app.config['MONGO_DB_NAME'] = MONGO_DB_NAME

    # Email Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    # MongoDB Connection
    try:
        mongo_client = pymongo.MongoClient(app.config['MONGO_URI'])
        db = mongo_client[app.config['MONGO_DB_NAME']]
        app.config['DB_CONNECTION'] = db
    except pymongo.errors.PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

    login_manager.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v2/',
        userinfo_endpoint='https://www.googleapis.com/oauth2/v2/userinfo',
        client_kwargs={'scope': 'openid email profile'}
    )

    app.oauth = oauth

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    from .profile import profile_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')

    return app
