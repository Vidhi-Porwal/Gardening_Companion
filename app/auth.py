from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required
import re
from .models import User

auth = Blueprint('auth', __name__)

# Regular expressions for validation
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'  # At least 8 characters, 1 letter, and 1 number
PHONE_REGEX = r'^\+?[0-9]{10,15}$'  # International format or 10-15 digits

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Use .get() to avoid KeyError
        identifier = request.form.get('identifier')  # username or phone
        password = request.form.get('password')

        if not identifier or not password:
            flash('Please provide both identifier and password.', 'danger')
            return redirect(url_for('auth.login'))

        # Proceed with login logic
        user = User.get_user_by_username_or_phone(identifier)  # Update this logic as per your app
        if user and check_password_hash(User.password_hash, password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
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

        # Regex validation
        if not re.match(EMAIL_REGEX, email):
            flash('Invalid email format. Please enter a valid email address.')
        elif not re.match(PASSWORD_REGEX, password):
            flash('Password must be at least 8 characters long and contain at least one letter and one number.')
        elif not re.match(PHONE_REGEX, phone_no):
            flash('Invalid phone number. It must be 10-15 digits and can include a leading "+" for international numbers.')
        elif User.get_user_by_email(email):
            flash('Email is already registered.')
        else:
            # For now, store passwords in plain text; replace with hashed passwords in production
            User.create_user(full_name, username, email, password, phone_no)
            flash('Account created successfully! Please log in.')
            return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
