from flask import render_template, session, redirect, url_for
from app import app
from app.auth import auth

app.register_blueprint(auth)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))  # Redirect if not logged in

    # Mock data for demonstration
    plants = [
        {"name": "Basil", "watering_schedule": "Every 3 days", "fertilizing_schedule": "Every 2 weeks"},
        {"name": "Roses", "watering_schedule": "Every 4 days", "fertilizing_schedule": "Every 3 weeks"}
    ]
    reminders = [
        {"task": "Water Basil", "due": "Tomorrow"},
        {"task": "Fertilize Roses", "due": "In 3 days"}
    ]
    return render_template('dashboard.html', plants=plants, reminders=reminders)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

