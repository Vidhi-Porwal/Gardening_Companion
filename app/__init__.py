from flask import Flask
from flask_login import LoginManager
import pymysql
import os

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.get_user_by_id(user_id)

def create_app():
    app = Flask(__name__)

    # Load configurations
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'DEV')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'Vidhi@3112')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'gardening_companion')

    # Set up MySQL connection
    def get_db_connection():
        return pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor
        )

    app.config['DB_CONNECTION'] = get_db_connection

    # Initialize extensions
    login_manager.init_app(app)
        

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app














































# ### init.py ###
# from flask import Flask
# from flask_login import LoginManager
# import pymysql
# import os
# from .dashboard import dashboard_bp
# import google.generativeai as genai

# # Initialize extensions
# login_manager = LoginManager()
# login_manager.login_view = "auth.login"

# @login_manager.user_loader
# def load_user(user_id):
#     from .models import User
#     return User.get_user_by_id(user_id)

# def create_app():
#     app = Flask(__name__)


#     # Option 1: Using an API Key
#     api_key = "****"
#     genai.configure(api_key=api_key)

#     # Example usage
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content("give me list of 100 indian common garden plants")
#     print(response.text)

#     # Load configurations
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'DEV')
#     app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
#     app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
#     app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'Vidhi@3112')
#     app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'gardening_companion')

#     # Set up MySQL connection
#     def get_db_connection():
#         return pymysql.connect(
#             host=app.config['MYSQL_HOST'],
#             user=app.config['MYSQL_USER'],
#             password=app.config['MYSQL_PASSWORD'],
#             database=app.config['MYSQL_DB'],
#             cursorclass=pymysql.cursors.DictCursor
#         )

#     app.config['DB_CONNECTION'] = get_db_connection

#     # Initialize extensions
#     login_manager.init_app(app)

#     # Register blueprints
#     from .routes import main
#     app.register_blueprint(main)

#     from .auth import auth
#     app.register_blueprint(auth, url_prefix='/auth')

#     app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

#     return app