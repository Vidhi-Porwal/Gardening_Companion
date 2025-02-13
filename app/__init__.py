# from flask import Flask , current_app
# from flask_login import LoginManager
# import pymongo
# import os
# from .models import User

# # Initialize Flask-Login
# login_manager = LoginManager()
# # login_manager.init_app(app)
# login_manager.login_view = "auth.login"  # Redirect to the login page if not authenticated

# # User loader for Flask-Login
# # @login_manager.user_loader
# # def load_user(user_id):
# #     from .models import User
# #     return User.get_user_by_id(user_id)
# @login_manager.user_loader
# def load_user(user_id):
#     db = current_app.config['DB_CONNECTION']
#     user = db.users.find_one({"_id": user_id})
#     if user:
#         return User(
#             id=user['_id'],
#             username=user['username'],
#             email=user['email'],
#             phone_no=user.get('phone_no'),
#             role=user.get('role', 'user')
#         )
#     return None

# def create_app():
#     """
#     Application Factory: Creates and configures the Flask app.
#     """
#     app = Flask(__name__)

#     # Load configurations
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'DEV')  # Fallback to 'DEV' for local development
#     app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://3.86.209.148:27017')
#     app.config['MONGO_DB_NAME'] = os.getenv('MONGO_DB_NAME', 'Gardening_Companion')

#     # Set up MongoDB connection
#     try:
#         mongo_client = pymongo.MongoClient(app.config['MONGO_URI'])
#         db = mongo_client[app.config['MONGO_DB_NAME']]
#         app.config['DB_CONNECTION'] = db
#     except pymongo.errors.PyMongoError as e:
#         print(f"Error connecting to MongoDB: {e}")
#         raise

#     # Initialize Flask extensions
#     login_manager.init_app(app)

#     # Register blueprints
#     from .routes import main  # Main routes for the application
#     app.register_blueprint(main)

#     from .auth import auth  # Authentication-related routes 
#     app.register_blueprint(auth, url_prefix='/auth')

#     from .dashboard import dashboard_bp  # Dashboard routes
#     app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

#     # # Optionally, add a test route for health checks
#     # @app.route('/ping', methods=['GET'])
#     # def health_check():
#     #     return "pong", 200

#     return app


from flask import Flask, current_app
from flask_login import LoginManager
import pymongo
import os
from bson import ObjectId
from dotenv import load_dotenv
from .models import User
from flask_dance.contrib.google import make_google_blueprint

# Load environment variables
load_dotenv()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    db = current_app.config['DB_CONNECTION']
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(
            id=str(user['_id']),
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

    # Load configurations
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'DEV')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://3.86.209.148:27017')
    app.config['MONGO_DB_NAME'] = os.getenv('MONGO_DB_NAME', 'Gardening_Companion')

    # Set up MongoDB connection
    try:
        mongo_client = pymongo.MongoClient(app.config['MONGO_URI'])
        db = mongo_client[app.config['MONGO_DB_NAME']]
        app.config['DB_CONNECTION'] = db
    except pymongo.errors.PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}")x
        raise

    # Initialize Flask extensions
    login_manager.init_app(app)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    from .auth import auth, google_blueprint  # Import google_blueprint
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(google_blueprint, url_prefix='/login')  # Register OAuth Google Login


    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app
