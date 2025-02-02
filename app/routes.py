##routes.py##
from flask import render_template, Blueprint, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = current_app.config['DB_CONNECTION']  # Access MongoDB connection

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
                # Check if username or email is already taken by another user
                existing_user = db.users.find_one({
                    "$or": [
                        {"username": username, "_id": {"$ne": current_user.id}},
                        {"email": email, "_id": {"$ne": current_user.id}}
                    ]
                })

                if existing_user:
                    flash('Username or email is already taken by another user.', 'danger')
                else:
                    # Update user data in MongoDB
                    db.users.update_one(
                        {"_id": current_user.id},
                        {"$set": {
                            "full_name": full_name,
                            "username": username,
                            "email": email,
                            "phone_no": phone_no,
                            "status": status
                        }}
                    )

                    # Update `current_user` attributes for immediate reflection
                    current_user.full_name = full_name
                    current_user.username = username
                    current_user.email = email
                    current_user.phone_no = phone_no
                    current_user.status = status

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
