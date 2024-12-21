from flask import render_template, request, redirect, url_for
from app import app

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
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
