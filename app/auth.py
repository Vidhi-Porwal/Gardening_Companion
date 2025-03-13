##auth.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.oauth2 import OAuth2ConsumerBlueprint
from flask_dance.consumer import oauth_error
from authlib.integrations.flask_client import OAuthError  
from .models import User  
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime  
import pymongo
from flask_login import current_user

import re
from .models import User
from flask_mail import Message
from . import mail

from .utils import generate_reset_token,verify_reset_token




auth = Blueprint('auth', __name__)

# Regular expressions for validation
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#_]{8,}$'  # At least 8 characters, 1 letter, and 1 number
PHONE_REGEX = r'^\+?[0-9]{10,15}$'
USERNAME_REGEX = r'^[A-Za-z][A-Za-z0-9_]{7,29}$'


# Set up insecure transport for development (remove in production)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Create Blueprint
auth = Blueprint("auth", __name__)

# Google OAuth Blueprint
google_blueprint = make_google_blueprint(
    scope=[
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ],
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to="auth.oauth_callback"  #  Must match the auth blueprint route
)

@auth.route("/login/google")  
def google_login():
    """Redirect the user to Google login."""
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("auth.oauth_callback"))  


@auth.route("/oauth_callback")
def oauth_callback():
    """Handle the callback after Google OAuth."""
    try:
        if not google.authorized:
            flash("Google authentication failed. Please try again.", "danger")
            return redirect(url_for("google.login"))

        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Failed to fetch user info from Google.", "danger")
            return redirect(url_for("auth.login"))

        user_info = resp.json()
        print("User info:", user_info)

        db = current_app.config['DB_CONNECTION']
        email = user_info.get("email")

        if not email:
            flash("No email found in Google account. Please use a valid account.", "danger")
            return redirect(url_for("auth.login"))

        # Check if user already exists in MongoDB
        user = db.users.find_one({"email": email})

        if not user:
            # Automatically sign up new users without a phone number
            inserted = db.users.insert_one({
                "email": email,
                "username": user_info.get("name"),
                "profile_pic": user_info.get("picture"),
                "phone_no": None,  # Phone number is initially empty
                "role": "user"  # Default role
            })
            user_id = inserted.inserted_id
            # Set phone_no to None for the new user.
            phone_no = None
        else:
            user_id = user["_id"]
            phone_no = user.get("phone_no")

        # Log the user in
        user_obj = User(
            id=str(user_id),
            email=email,
            username=user_info.get("name"),
            phone_no=phone_no
        )
        login_user(user_obj)

        # If phone number is missing, redirect to a page to ask for it
        if not phone_no:
            flash("Please update your phone number.", "info")
            return redirect(url_for("auth.update_phone"))

        flash("Login successful!", "success")
        return redirect(url_for("dashboard.dashboard"))

    except pymongo.errors.PyMongoError as db_error:
        print(f"MongoDB Error: {db_error}")
        flash("Database error occurred. Please try again later.", "danger")
        return redirect(url_for("auth.login"))

    except Exception as e:
        print(f"Unexpected Error: {e}")
        flash("An unexpected error occurred. Please try again.", "danger")
        return redirect(url_for("auth.login"))



@auth.route("/update_phone", methods=["GET", "POST"])
@login_required
def update_phone():
    """Allow users to update their phone number."""
    if request.method == "POST":
        phone_no = request.form.get("phone_no")
        
        if not phone_no:
            flash("Phone number is required!", "danger")
            return redirect(url_for("auth.update_phone"))

        if not re.match(PHONE_REGEX, phone_no):
            flash('Invalid phone number.', 'danger')
            return redirect(url_for("auth.update_phone"))

        db = current_app.config['DB_CONNECTION']
        db.users.update_one({"email": current_user.email}, {"$set": {"phone_no": phone_no}})
        
        flash("Phone number updated successfully!", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("update_phone.html")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        if not identifier or not password:
            flash('Please provide both username/email/phone and password.', 'danger')
            return redirect(url_for('auth.login'))

        db = current_app.config['DB_CONNECTION']
        user = User.find_by_identifier(db, identifier)

        if not user:
            flash('Username or email not found.', 'danger')  # Specific error for username/email
            return redirect(url_for('auth.login'))

        if not User.check_password(user, password):
            flash('Incorrect password. Please try again.', 'danger')  # Specific error for password
            return redirect(url_for('auth.login'))

        # Create user session
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
        elif not re.match(PASSWORD_REGEX, password):
            flash('Password must be at least 8 characters long and contain at least one letter and one number.', 'danger')
        elif not re.match(PHONE_REGEX, phone_no):
            flash('Invalid phone number.', 'danger')
        elif not re.match(USERNAME_REGEX, username):
            flash('Invalid username.', 'danger')
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



@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        db = current_app.config['DB_CONNECTION']
        user = db.users.find_one({"email": email})
        if user:
            token = generate_reset_token(email)
            reset_link = url_for("auth.reset_password", token=token, _external=True)

            msg = Message("Password Reset Request", sender="your_email@gmail.com", recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_link}"

            msg.html = f"""
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}" target="_blank"><strong>Reset Password</strong></a></p>
                <p>If you did not request this, please ignore this email.</p>
            """
            try:
                mail.send(msg)
                flash("A password reset link has been sent to your email.", "info")
                print(f" Reset Email Sent: {reset_link}")  # Debugging
            except Exception as e:
                print(f" Error sending email: {e}")  # Debugging
                flash("Error sending email. Try again later.", "danger")
        else:
            flash("Email not found.", "danger")

    return render_template("forgot_password.html")

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    db = current_app.config['DB_CONNECTION']
    email = verify_reset_token(token)  # Ensure the token is valid

    if not email:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not re.match(password_pattern, new_password):
            flash('Password must be at least 8 characters long and contain at least one letter and one number.', 'danger')
            return redirect(url_for("auth.reset_password", token=token))

        if new_password != confirm_password:
            flash("Passwords do not match. Please try again.", "danger")
            return redirect(url_for("auth.reset_password", token=token))

        hashed_password = generate_password_hash(new_password)  

        db.users.update_one({"email": email}, {"$set": {"password_hash": hashed_password}})  

        flash("Your password has been updated! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)

    
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('auth.login'))
