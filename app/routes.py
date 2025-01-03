### routes.py ###
from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Retrieve form data
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        phone_no = request.form.get('phone_no')
        status = request.form.get('status') or current_user.status  # Retain current status if not provided

        # Validate and update the user's data
        if not full_name or not username or not email or not phone_no:
            flash('All fields except status are required.', 'danger')
        else:
            try:
                # Use the update_user method from the User model
                User.update_user(
                    user_id=current_user.id,
                    full_name=full_name,
                    username=username,
                    email=email,
                    phone_no=phone_no
                )

                # Update `current_user` attributes for immediate reflection
                current_user.full_name = full_name
                current_user.username = username
                current_user.email = email
                current_user.phone_no = phone_no

                flash('Profile updated successfully!', 'success')
            except Exception as e:
                flash('An error occurred while updating your profile. Please try again.', 'danger')
                print(f"Error updating profile: {e}")

        # Redirect back to profile to refresh the page
        return redirect(url_for('main.profile'))

    # Render the profile page with current user data
    return render_template('profile.html', user=current_user)

@main.route('/tips_tricks')
def tips_tricks():
    return render_template('tips_tricks.html')