### routes.py ###
from flask import render_template, Blueprint
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/tips_tricks')
def tips_tricks():
    return render_template('tips_tricks.html')