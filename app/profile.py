from flask import render_template, Blueprint, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user

profile_bp = Blueprint('profile', __name__)  # Define a separate blueprint for profile-related routes

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
            try:
                # Check if username is already taken by another user
                existing_user = db.users.find_one({
                    "username": username,
                    "_id": {"$ne": current_user.id}
                })

                if existing_user:
                    flash('Username is already taken by another user.', 'danger')
                else:
                    # Update user data in MongoDB (excluding email)
                    db.users.update_one(
                        {"_id": current_user.id},
                        {"$set": {
                            "full_name": full_name,
                            "username": username,
                            "phone_no": phone_no
                        }}
                    )

                    # Update `current_user` attributes for immediate reflection
                    current_user.full_name = full_name
                    current_user.username = username
                    current_user.phone_no = phone_no

                    flash('Profile updated successfully!', 'success')

            except Exception as e:
                flash('An error occurred while updating your profile. Please try again.', 'danger')
                print(f"Error updating profile: {e}")

        # Redirect back to profile to refresh the page
        return redirect(url_for('profile.profile'))

    # Render the profile page with current user data
    return render_template('profile.html', user=current_user)
    