### dashboard.py ###
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import UserPlant, PlantInfo
import google.generativeai as genai
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        # Fetch user plants and all plants
        user_plants = UserPlant.get_user_plants(current_user.id)
        plants = PlantInfo.get_all_plants()

        if request.method == 'POST':
            # Handle adding a plant
            if 'add_plant' in request.form:
                plant_id = request.form.get('plant_id')
                if plant_id:
                    UserPlant.add_plant_to_user(current_user.id, plant_id, quantity=1)
                return redirect(url_for('dashboard.dashboard'))

            # Handle removing a plant
            if 'remove_plant' in request.form:
                plant_id = request.form.get('plant_id')
                print(f"Removing plant with ID: {plant_id}")  # Debug log
                if plant_id:
                    success = UserPlant.remove_plant_from_user(current_user.id, plant_id)
                    if not success:
                        print("plant not removed")
                        # flash("Failed to remove the plant. Please try again.", "danger")
                    else:
                        print("plant removed successfully")
                        # flash("Plant removed successfully.", "success")
                return redirect(url_for('dashboard.dashboard'))


        return render_template('dashboard.html', user_plants=user_plants, plants=plants, chatbot_open=chatbot_open,
            chat_history=chat_history)
    except Exception as e:
        print(f"Error in dashboard: {e}")
        # return render_template('error.html', error_message="Something went wrong. Please try again later."), 500
        return render_template('login.html')
genai.configure(api_key="AIzaSyCF9pTtirypeeHUMTohJiepKntkuuP07hI")
model = genai.GenerativeModel("gemini-1.5-flash")
chatbot_open = False  # Global variable to track chatbot visibility
chat_history = []  # Global variable to store chat history
def chatbot_response(prompt, chat_history=[]):
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

# Route to toggle the chatbot visibility
@dashboard_bp.route('/chatbot_toggle', methods=['POST'])
@login_required
def chatbot_toggle():
    global chatbot_open
    chatbot_open = not chatbot_open
    return redirect(url_for('dashboard.dashboard'))

# Route to handle chatbot interactions
@dashboard_bp.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    global chat_history

    # Get user input from form
    user_message = request.form.get("message")
    if not user_message:
        return redirect(url_for('dashboard.dashboard'))

    # Add user message to chat history
    chat_history.append(f"You: {user_message}")

    # Generate chatbot response
    chatbot_reply = chatbot_response(user_message, chat_history)
    chat_history.append(f"Plantie 🌼: {chatbot_reply}")

    return redirect(url_for('dashboard.dashboard'))











































# @dashboard_bp.route('/', methods=['POST','GET'])
# @login_required
# def dashboard():
#     user_plants = UserPlant.get_user_plants(current_user.id)    


#     plants = PlantInfo.get_all_plants() # Fetch all plants from the database

    
#     plant_id = request.form.get('plant_id')
#     print (plant_id)
#     UserPlant.add_plant_to_user(current_user.id, plant_id, quantity=1)
#     return render_template('dashboard.html', user_plants=user_plants, plants=plants)

# @dashboard_bp.route('/search', methods=['GET', 'POST'])
# @login_required
# def search_plants():
#     if request.method == 'POST':
#         search_query = request.form.get('search')
#         plants = UserPlant.search_plants(search_query)
#         return render_template('search_results.html', plants=plants)
#     return render_template('search.html')

# @dashboard_bp.route('/add_plant/<int:plant_id>', methods=['POST'])
# @login_required
# def add_plant_to_user(plant_id):
#     UserPlant.add_plant_to_user(current_user.id, plant_id, quantity=1)
#     return redirect(url_for('dashboard.dashboard'))

# @dashboard_bp.route('/remove_plant/<int:plant_id>', methods=['POST'])
# @login_required
# def remove_plant_from_user(plant_id):
#     UserPlant.remove_plant_from_user(current_user.id, plant_id)
#     return redirect(url_for('dashboard.dashboard'))

# @dashboard_bp.route('/get_plants', methods=['GET'])
# def get_plants():
#     import pdb; pdb.set_trace();
#     try:
#         plants = PlantInfo.get_all_plants()  # Fetch all plants from the database
#         print("plants")
#         return jsonify(plants), 200
#     except Exception as e:
#         print(f"Error fetching plants: {e}")
#         return jsonify({'error': 'Failed to fetch plant data'}), 500

