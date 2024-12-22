from flask import render_template, Blueprint
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/dashboard')
# @login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/login')
def login():
    return render_template('login.html')

@main.route('/signup')
def signup():
    return render_template('signup.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/track_plants')
@login_required
def track_plants():
    return render_template('track_plants.html')

@main.route('/reminders')
@login_required
def reminders():
    return render_template('reminders.html')

@main.route('/tips_tricks')
def tips_tricks():
    return render_template('tips_tricks.html')
