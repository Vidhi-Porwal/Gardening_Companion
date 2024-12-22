import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

auth = Blueprint('auth', __name__)

# Mock database for demonstration (Replace with actual database later)
users = {}

# Helper function: Validate email
def is_valid_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email)

# Helper function: Validate password
def is_valid_password(password):
    return len(password) >= 8 and re.search(r'\d', password) and re.search(r'[A-Za-z]', password)

# Signup Route
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile_no = request.form['mobile_no']

        # Validate inputs
        if not full_name or not username or not password or not email or not mobile_no:
            flash('All fields are required!', 'danger')
        elif username in users:
            flash('Username already exists!', 'danger')
        elif mobile_no in [user['mobile_no'] for user in users.values()]:
            flash('Mobile number already registered!', 'danger')
        elif not is_valid_email(email):
            flash('Invalid email format!', 'danger')
        elif not is_valid_password(password):
            flash('Password must be at least 8 characters long, include letters and numbers!', 'danger')
        else:
            # Save user
            users[username] = {
                'full_name': full_name,
                'password': password,
                'email': email,
                'mobile_no': mobile_no
            }
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('signup.html')

# Login Route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        # Check user by username or mobile number
        user = next((user for user in users.values() if (user['mobile_no'] == identifier or user == identifier)), None)

        if not user or user['password'] != password:
            flash('Invalid credentials!', 'danger')
        else:
            session['user'] = user
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))

    return render_template('login.html')

# Logout Route
@auth.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('auth.login'))
