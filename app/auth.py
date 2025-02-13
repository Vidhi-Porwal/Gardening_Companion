# #auth.py


# from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import login_user, logout_user, login_required
# import re
# from bson import ObjectId
# from .models import User

# auth = Blueprint('auth', __name__)

# # Regular expressions for validation
# EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
# PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#_]{8,}$'  # At least 8 characters, 1 letter, and 1 number
# PHONE_REGEX = r'^\+?[0-9]{10,15}$'

# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         identifier = request.form.get('identifier')
#         password = request.form.get('password')

#         if not identifier or not password:
#             flash('Please provide both identifier and password.', 'danger')
#             return redirect(url_for('auth.login'))

#         # Access MongoDB
#         try:
#             db = current_app.config['DB_CONNECTION']
#             user = db.users.find_one({
#                 "$or": [
#                     {"username": identifier},
#                     {"email": identifier},
#                     {"phone_no": identifier}
#                 ]
#             })
#         except Exception as e:
#             flash('Database error. Please try again later.', 'danger')
#             return redirect(url_for('auth.login'))

#         if user and check_password_hash(user['password_hash'], password):
#             user_obj = User(
#                 id=str(user['_id']),
#                 username=user['username'],
#                 email=user['email'],
#                 phone_no=user.get('phone_no'),
#                 role=user.get('role', 'user')
#             )
#             login_user(user_obj)

#             # Redirect based on role if necessary
#             role_redirects = {
#                 'admin': 'dashboard.admin_dashboard',
#                 'user': 'dashboard.dashboard'
#             }
#             return redirect(url_for(role_redirects.get(user_obj.role, 'dashboard.dashboard')))
#         else:
#             flash('Invalid credentials, please try again.', 'danger')
#             return redirect(url_for('auth.login'))
#     return render_template('login.html')

# @auth.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         full_name = request.form['full_name']
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
#         phone_no = request.form['phone_no']

#         if not re.match(EMAIL_REGEX, email):
#             flash('Invalid email format.', 'danger')
#         elif not re.match(PASSWORD_REGEX, password):
#             flash('Password must be at least 8 characters long and contain at least one letter and one number.', 'danger')
#         elif not re.match(PHONE_REGEX, phone_no):
#             flash('Invalid phone number.', 'danger')
#         else:
#             db = current_app.config['DB_CONNECTION']
#             if db.users.find_one({"email": email}):
#                 flash('Email is already registered.', 'danger')
#             elif db.users.find_one({"username": username}):
#                 flash('Username is already taken.', 'danger')
#             else:
#                 hashed_password = generate_password_hash(password)
#                 db.users.insert_one({
#                     "full_name": full_name,
#                     "username": username,
#                     "email": email,
#                     "password_hash": hashed_password,
#                     "phone_no": phone_no,
#                     "role": "user",
#                     "status": "active"
#                 })
#                 flash('Account created successfully! Please log in.', 'success')
#                 return redirect(url_for('auth.login'))
#     return render_template('signup.html')

# @auth.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have successfully logged out.', 'success')
#     return redirect(url_for('auth.login'))


from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
import re
from bson import ObjectId
from .models import User

auth = Blueprint('auth', __name__)

# Regular expressions for validation
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#_]{8,}$'  # At least 8 characters, 1 letter, and 1 number
PHONE_REGEX = r'^\+?[0-9]{10,15}$'

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        if not identifier or not password:
            flash('Please provide both identifier and password.', 'danger')
            return redirect(url_for('auth.login'))

        db = current_app.config['DB_CONNECTION']
        user = User.find_by_identifier(db, identifier)

        if user and User.check_password(user, password):
            user_obj = User(
                id=str(user['_id']),
                username=user['username'],
                email=user['email'],
                phone_no=user.get('phone_no'),
                role=user.get('role', 'user')
            )
            login_user(user_obj)

            # Redirect based on role
            role_redirects = {
                'admin': 'dashboard.dashboard',
                'user': 'dashboard.dashboard'
            }
            return redirect(url_for(role_redirects.get(user_obj.role, 'dashboard.dashboard')))
        else:
            flash('Invalid credentials, please try again.', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone_no = request.form['phone_no']

        if not re.match(EMAIL_REGEX, email):
            flash('Invalid email format.', 'danger')
            flash('Invalid email format.', 'danger')
        elif not re.match(PASSWORD_REGEX, password):
            flash('Password must be at least 8 characters long and contain at least one letter and one number.', 'danger')
            flash('Password must be at least 8 characters long and contain at least one letter and one number.', 'danger')
        elif not re.match(PHONE_REGEX, phone_no):
            flash('Invalid phone number.', 'danger')
            flash('Invalid phone number.', 'danger')
        else:
            db = current_app.config['DB_CONNECTION']
            if User.find_by_email(db, email):
                flash('Email is already registered.', 'danger')
            elif User.find_by_username(db, username):
                flash('Username is already taken.', 'danger')
            else:
                User.create_user(db, full_name, username, email, password, phone_no)
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('auth.login'))