import re
from flask import render_template, Blueprint, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from bson import ObjectId

profile_bp = Blueprint('profile', __name__)  # Define a separate blueprint for profile-related routes

# Regular expressions for validation
PHONE_REGEX = r'^\+?[0-9]{10,15}$'
USERNAME_REGEX = r'^[A-Za-z][A-Za-z0-9_]{4,29}$'
FULL_NAME_REGEX = r'^[A-Za-z\s]{2,50}$'  # Only alphabetic characters and spaces, 2-50 characters

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def profile():
    db = current_app.config['DB_CONNECTION']  # Access MongoDB connection

    if request.method == 'POST':
        # Retrieve form data (excluding email)
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        phone_no = request.form.get('phone_no')

        # Validate required fields
        if not full_name or not username or not phone_no:
            flash('All fields except email are required.', 'danger')
        else:
            # Validate full_name using regex
            if not re.match(FULL_NAME_REGEX, full_name):
                flash('Full name must only contain alphabetic characters and spaces (2-50 characters).', 'danger')
                return redirect(url_for('profile.profile'))

            # Validate username using regex
            if not re.match(USERNAME_REGEX, username):
                flash('Username must start with a letter and be 8-30 characters long, only containing alphanumeric characters and underscores.', 'danger')
                return redirect(url_for('profile.profile'))

            # Validate phone number using regex
            if not re.match(PHONE_REGEX, phone_no):
                flash('Phone number must be between 10 to 15 digits, with an optional leading "+" symbol.', 'danger')
                return redirect(url_for('profile.profile'))

            try:
                # Check if username or phone number is already taken by another user
                existing_user = db.users.find_one({
                    "$or": [
                        {"username": username, "_id": {"$ne": ObjectId(current_user.id)}},  # Check username
                        {"phone_no": phone_no, "_id": {"$ne": ObjectId(current_user.id)}}  # Check phone number
                    ]
                })

                if existing_user:
                    if existing_user.get('username') == username:
                        flash('Username is already taken by another user.', 'danger')
                    elif existing_user.get('phone_no') == phone_no:
                        flash('Phone number is already taken by another user.', 'danger')
                else:
                    # Update user data in MongoDB (excluding email)
                    result = db.users.update_one(
                        {"_id": ObjectId(current_user.id)},  # Ensure the ID is an ObjectId
                        {"$set": {
                            "full_name": full_name,
                            "username": username,
                            "phone_no": phone_no
                        }}
                    )

                    if result.modified_count > 0:
                        # Update `current_user` attributes for immediate reflection
                        current_user.full_name = full_name
                        current_user.username = username
                        current_user.phone_no = phone_no

                        flash('Profile updated successfully!', 'success')
                    else:
                        flash('No changes were made to your profile.', 'warning')

            except Exception as e:
                flash(f'An error occurred while updating your profile. Please try again. Error: {e}', 'danger')
                print(f"Error updating profile: {e}")

        # Redirect back to profile to refresh the page
        return redirect(url_for('profile.profile'))

    # Render the profile page with current user data
    return render_template('profile.html', user=current_user)
