from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import google.generativeai as genai
from functools import wraps
import os
from bson.objectid import ObjectId
from .models import User

# Initialize blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Configure the Gemini API
api_key = os.getenv("GENAI_API_KEY", "YOUR_GENAI_API_KEY")
genai.configure(api_key=api_key)

# Utility: Role-based access decorator
def role_required(role):
    """
    Restricts access based on user roles.
    Args:
        role (str): Required role ('admin', 'client', etc.).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You need to log in to access this page.", "error")
                return redirect(url_for("auth.login"))
            if current_user.role != role:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("main.index"))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def ensure_default_garden(user_id):
    default_garden = db.gardens.find_one({"user_id": ObjectId(user_id), "name": "My Garden"})
    if not default_garden:
        db.gardens.insert_one({
            "name": "My Garden",
            "user_id": ObjectId(user_id)
        })

# Dashboard Route
@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required('user')
def dashboard():
    try:
        # Access the MongoDB database
        db = current_app.config['DB_CONNECTION']

        # Fetch user's plants and all available plants
        user_plants = list(db.garden_plant.find({"user_id": current_user.id}))
        plants = list(db.plants.find())

        gemini_response = None

        # Handle POST requests
        if request.method == 'POST':
            # Add a plant to the user's garden
            if 'add_plant' in request.form:
                plant_id = request.form.get('plant_id')
                plant_id = ObjectId(plant_id)
                if plant_id:
                    try:
                        # Fetch plant information
                        plant_info = db.plants.find_one({"_id": plant_id})
                        if not plant_info:
                            flash("Plant not found in the database.", "warning")
                            return redirect(url_for('dashboard.dashboard'))

                        plant_common_name = plant_info.get("common_name", "Unknown")
                        model = genai.GenerativeModel("gemini-1.5-flash")

                        # Prepare the prompt for Gemini API
                        prompt = (f"Give me watering and fertilizing schedule for {plant_common_name}, "
                                  "I just want numbers like in how many days return only a number, "
                                  "also give me the amount of sunlight it needs. In sunlight, give: "
                                  "1 for full sunlight, 2 for partial sunlight, 3 for no sunlight. "
                                  "Also give me the type of fertilizer recommended.")
                        response = model.generate_content(prompt)
                        gemini_response = response.text

                        # Parse and store the response
                        data = parse_gemini_response(gemini_response)
                        if data:
                            db.user_plants.insert_one({
                                "user_id": current_user.id,
                                "plant_id": plant_id,
                                "watering": data['watering'],
                                "fertilizing": data['fertilizing'],
                                "sunlight": data['sunlight'],
                                "fertilizer_type": data['fertilizer_type'],
                                "plant_common_name": plant_common_name
                            })
                            flash(f"{plant_common_name} has been added to your garden!", "success")
                        else:
                            flash("Failed to parse plant care details.", "warning")
                    except Exception as e:
                        flash(f"Error adding plant: {str(e)}", "danger")

                return redirect(url_for('dashboard.dashboard'))

            # Remove a plant from the user's garden
            if 'remove_plant' in request.form:
                plant_id = request.form.get('plant_id')
                if plant_id:
                    result = db.user_plants.delete_one({"user_id": current_user.id, "plant_id": plant_id})
                    if result.deleted_count == 0:
                        flash("Failed to remove plant.", "danger")
                    else:
                        flash("Plant removed successfully.", "success")
                    return redirect(url_for('dashboard.dashboard'))

        # Render the dashboard template
        return render_template('dashboard.html', user_plants=user_plants, plants=plants, gemini_response=gemini_response)

    except Exception as e:
        print(f"Error in dashboard: {e}")
        return render_template('error.html', error_message="Something went wrong. Please try again later."), 500


# Helper Function: Parse Gemini Response
def parse_gemini_response(response_text):
    """
    Parse the response from Gemini API to extract plant care details.
    """
    data = {}
    try:
        for line in response_text.split("\n"):
            if "Watering:" in line:
                data['watering'] = int(line.split(":")[1].strip())
            elif "Fertilizing:" in line:
                data['fertilizing'] = int(line.split(":")[1].strip())
            elif "Sunlight:" in line:
                data['sunlight'] = int(line.split(":")[1].strip())
            elif "Fertilizer type:" in line:
                data['fertilizer_type'] = line.split(":")[1].strip()
    except Exception as e:
        print(f"Error parsing response: {e}")
    return data



@dashboard_bp.route("/add_garden", methods=["POST"])
def add_garden():
    garden_name = request.form.get("garden_name")
    user_id = current_user.id  # Replace with your user session ID retrieval
    if garden_name and user_id:
        db.garden.insert_one({
            "name": garden_name,
            "user_id": ObjectId(user_id),
            "$set": { "updated_at": datetime.now() }
        })
        flash("Garden added successfully!")
    return redirect(url_for("dashboard.dashboard"))


# Chatbot Toggle Route
@dashboard_bp.route('/chatbot_toggle', methods=['POST'])
@login_required
def chatbot_toggle():
    global chatbot_open
    chatbot_open = not chatbot_open
    return redirect(url_for('dashboard.dashboard'))


# Chatbot Interaction Route
@dashboard_bp.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    global chat_history

    # Get user input from the form
    user_message = request.form.get("message")
    if not user_message:
        return redirect(url_for('dashboard.dashboard'))

    # Add user message to chat history
    chat_history.append(f"You: {user_message}")

    # Generate chatbot response
    chatbot_reply = chatbot_response(user_message, chat_history)
    chat_history.append(f"Plantie 🌼: {chatbot_reply}")

    return redirect(url_for('dashboard.dashboard'))


# Generate Chatbot Response
def chatbot_response(prompt, chat_history=[]):
    model = genai.GenerativeModel("gemini-1.5-flash")
    if chat_history:
        prompt = "\n".join(chat_history) + "\n" + prompt

    concise_prompt = f"Please answer briefly: {prompt}"
    try:
        response = model.generate_content(concise_prompt)
        if response and hasattr(response, "text") and response.text:
            return response.text
        return "Sorry, I couldn't generate a response. Try again!"
    except Exception as e:
        return "Error occurred while processing your request. Please try again!"
