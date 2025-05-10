from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from functools import wraps
from .models import User, Plant, Garden, GardenPlant, Age, ChatSession, GeminiHelper, Chatbot, PlantRequest
from bson.objectid import ObjectId
import google.generativeai as genai
from app.tasks import send_email_task
from datetime import datetime, timedelta

import logging

dashboard_bp = Blueprint('dashboard', __name__)

def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("You need to log in to access this page.", "error")
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("auth.login"))
            return func(*args, **kwargs)
        return wrapper
    return decorator

def redirect_to_dashboard(garden_id):
    return redirect(url_for("dashboard.dashboard", garden_id=garden_id))

@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required('user', 'admin')
def dashboard():
    try:
        default_garden_id = Garden.ensure_default_garden(current_user.id)
        garden_id = request.form.get('garden_id') or request.args.get('garden_id') or default_garden_id
        chat_session = ChatSession(current_user.id)
        user_garden = Garden.get_user_gardens(current_user.id)

        if not garden_id and user_garden:
            garden_id = str(user_garden[0]['_id'])

        try:
            garden_obj_id = ObjectId(garden_id)
        except:
            garden_obj_id = ObjectId(default_garden_id)

        final_plants = GardenPlant.get_user_plants(current_user.id, garden_obj_id)
        plants = Plant.get_all_plants()
        age = Age.get_all_ages()
        gemini_response = None

        if request.method == 'POST':
            if 'select_garden' in request.form:
                garden_id = request.form.get('garden_id') or default_garden_id
                return redirect_to_dashboard(garden_id)

            if 'add_plant' in request.form:
                plant_id = request.form.get('plant_id')
                age_id = request.form.get('age_id')

                if plant_id:
                    plant_info = Plant.get_plant_by_id(plant_id)
                    if not plant_info:
                        flash("Plant not found in the database.", "warning")
                        return redirect_to_dashboard(garden_id)

                    plant_common_name = plant_info.get("commonName", "Unknown")

                    if all(key in plant_info for key in ["watering", "fertilizing", "sunlight", "fertilizer_type", "soil_type", "change_soil"]):
                        data = {
                            "watering": plant_info["watering"],
                            "fertilizing": plant_info["fertilizing"],
                            "sunlight": plant_info["sunlight"],
                            "fertilizer_type": plant_info["fertilizer_type"],
                            "soil_type": plant_info["soil_type"],
                            "change_soil": plant_info["change_soil"],
                            "plant_common_name": plant_common_name
                        }
                    else:
                        try:
                            response_text = GeminiHelper.get_plant_care_info(plant_common_name)
                            gemini_response = response_text
                            data = GeminiHelper.parse_gemini_response(gemini_response)
                            data["plant_common_name"] = plant_common_name
                            Plant.update_plant(plant_id, data)
                        except Exception as e:
                            current_app.logger.error(f"GeminiHelper error: {e}")
                            flash("Could not retrieve plant care info. Please try again later.", "danger")
                            return redirect_to_dashboard(garden_id)

                    result = GardenPlant.add_plant_to_garden(
                        current_user.id,
                        garden_obj_id,
                        plant_id,
                        age_id,
                        data
                    )

                    db = current_app.config['DB_CONNECTION']
                    user = db.users.find_one({"_id": ObjectId(current_user.id)})
                    if user and result != "incremented":
                        subject = f"New Plant Added to Your Garden: {plant_common_name}"
                        body = f"""
Hello {user.get('full_name', 'Gardener')},

A new plant has been added to your garden:

🌱 Common Name: {plant_common_name}
💧 Watering every {data['watering']} days
🌞 Sunlight requirement: {data['sunlight']}
🌾 Fertilizer: {data['fertilizer_type']}
🪴 Soil Type: {data['soil_type']}
♻️ Change soil every {data['change_soil']} months

Happy Gardening! 🌼

- Garden Team
"""
                        send_email_task.delay(subject=subject, recipients=[user['email']], body=body)

                        try:
                            watering_days = int(data['watering'])
                            fertilizing_days = int(data['fertilizing'])
                            soil_change_days = int(data['change_soil']) * 30
                            full_name = user.get('full_name', 'Gardener')
                            email = user['email']

                            send_email_task.apply_async(
                                args=[f"🌿 Reminder: Water {plant_common_name}", [email], f"Hi {full_name},\n\nThis is your reminder to 💧 water your {plant_common_name} today!"],
                                eta=datetime.utcnow() + timedelta(days=watering_days)
                            )
                            send_email_task.apply_async(
                                args=[f"🌿 Reminder: Fertilize {plant_common_name}", [email], f"Hi {full_name},\n\nThis is your reminder to 🌾 fertilize your {plant_common_name} today!"],
                                eta=datetime.utcnow() + timedelta(days=fertilizing_days)
                            )
                            send_email_task.apply_async(
                                args=[f"🌿 Reminder: Change Soil for {plant_common_name}", [email], f"Hi {full_name},\n\n🪴 It's time to change the soil for your {plant_common_name}!"],
                                eta=datetime.utcnow() + timedelta(days=soil_change_days)
                            )
                        except Exception as e:
                            current_app.logger.error(f"Reminder scheduling error: {e}")

                    flash(f"{plant_common_name} has been added to your garden!", "success")
                return redirect_to_dashboard(garden_obj_id)

            if 'remove_plant' in request.form:
                plant_id = request.form.get('plant_id')
                age_id = request.form.get('age_id')
                result = GardenPlant.remove_plant_from_garden(current_user.id, garden_obj_id, plant_id, age_id)

                if result == "decremented":
                    flash("Plant quantity decreased.", "success")
                elif result == "removed":
                    flash("Plant removed completely.", "success")
                else:
                    flash("Plant not found.", "danger")

                return redirect_to_dashboard(garden_obj_id)

        return render_template(
            'dashboard.html',
            user_plants=final_plants,
            plants=plants,
            user_role=current_user.role,
            user_garden=user_garden,
            selected_garden=str(garden_obj_id),
            gemini_response=gemini_response,
            chatbot_open=chat_session.is_open,
            chat_history=chat_session.chat_history,
            age=age,
            garden_id=str(garden_obj_id)
        )
    except Exception as e:
        current_app.logger.error(f"Error in dashboard: {e}")
        return render_template('error.html', error_message="Something went wrong. Please try again later."), 500

@dashboard_bp.route("/add_garden", methods=["POST"])
@login_required
def add_garden():
    garden_name = request.form.get("garden_name")
    user_gardens = Garden.get_user_gardens(current_user.id)
    max_gardens_allowed = 2

    if len(user_gardens) >= max_gardens_allowed:
        flash("You’ve reached the limit of 2 gardens. Upgrade your plan or manage your existing gardens.", "warning")
        return redirect(url_for("dashboard.garden_limit_info"))

    if garden_name:
        new_garden_id = Garden.add_garden(current_user.id, garden_name)
        if new_garden_id:
            flash("Garden added successfully!", "success")
            return redirect_to_dashboard(new_garden_id)
        else:
            flash("Error: Garden name already exists.", "danger")

    return redirect_to_dashboard(default_garden_id)

@dashboard_bp.route("/garden_limit_info", methods=["GET"])
@login_required
def garden_limit_info():
    return render_template("garden_limit_info.html")

@dashboard_bp.route('/delete_garden/<garden_id>', methods=['DELETE'])
@login_required
def delete_garden(garden_id):
    success = Garden.delete_garden(current_user.id, garden_id)
    return jsonify({"success": success})

@dashboard_bp.route('/chatbot_toggle', methods=['POST'])
@login_required
def chatbot_toggle():
    chat_session = ChatSession(current_user.id)
    chat_session.toggle_chat()
    return redirect_to_dashboard(request.form.get("garden_id") or Garden.ensure_default_garden(current_user.id))

@dashboard_bp.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    chat_session = ChatSession(current_user.id)
    user_message = request.form.get("message", "").strip()

    if not user_message:
        return redirect_to_dashboard(request.form.get("garden_id") or Garden.ensure_default_garden(current_user.id))

    garden_id = request.args.get("garden_id") or request.form.get("garden_id")
    if not garden_id:
        garden_id = Garden.ensure_default_garden(current_user.id)

    chat_session.add_message("User", user_message)
    response = Chatbot.generate_response(
        prompt=user_message,
        chat_history=chat_session.chat_history,
        user_id=current_user.id,
        garden_id=garden_id
    )
    chat_session.add_message("Plantie 🌼", response)

    return redirect_to_dashboard(garden_id)

@dashboard_bp.route('/request_plant', methods=['GET', 'POST'])
@login_required
def request_plant():
    if request.method == 'POST':
        plant_name = request.form.get("plantName", "").strip()
        plant_description = request.form.get("plantDescription", "").strip()

        if not plant_name:
            flash("Plant name is required!", "danger")
            return redirect(url_for('dashboard.request_plant'))

        existing_plant = Plant.get_plant_by_name(plant_name)
        if existing_plant:
            flash("This plant is already available in the database!", "warning")
            return redirect(url_for('dashboard.request_plant'))

        PlantRequest.create_request(current_user.id, plant_name, plant_description)
        flash("Your plant request has been submitted for approval!", "success")
        return redirect_to_dashboard(Garden.ensure_default_garden(current_user.id))

    return render_template('request_plant.html')
