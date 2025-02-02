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

api_key = os.getenv("GENAI_API_KEY", "AIzaSyCF9pTtirypeeHUMTohJiepKntkuuP07hI")  # Use environment variable for API key

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


            # if 'show_plant' in request.form:
            #     plant_id = request.form.get('plant_id')
            #     if plant_id:
            #         result = PlantInfo.get_plant_by_id(plant_id)
            #         if not result:
            #             print("Plant not displayed")
            #         else:
            #             print("Plant displayed")
            #         return redirect(url_for('dashboard.dashboard'),result = result, plant_id = plant_id)

        # Render the dashboard page with all relevant data
        return render_template ('dashboard.html', user_plants=user_plants, plants=plants, gemini_response=gemini_response, chatbot_open=chat_session.is_open,  # Updated to use chat_session
            chat_history=chat_session.chat_history )


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

# genai.configure(api_key="")
model = genai.GenerativeModel("gemini-1.5-flash")

class ChatSession:
    def __init__(self):
        self.chat_history = []
        self.is_open = False

    def add_message(self, role, content):
        self.chat_history.append({"role": role, "content": content})

chat_session = ChatSession()

def create_structured_prompt(user_input, chat_history):
    # Create a more specific prompt structure
    base_prompt = """
    As a plant expert, provide detailed, specific answers about:
    - Plant care and maintenance
    - Plant diseases and treatments
    - Gardening techniques
    - Plant identification
    - Botanical information
    
    Format your response as:
    1. Direct answer to the question
    2. Additional relevant details
    
    if answer is not plant specific reply: please ask plant specific questions!!
    
    Previous context:
    {context}
    
    Current question: {question}
    """
    
    # Format the context from chat history
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-15:]])  # Last 15 messages
    return base_prompt.format(context=context, question=user_input)

def chatbot_response(prompt, chat_history):
    try:
        # Create structured prompt
        full_prompt = create_structured_prompt(prompt, chat_history)
        
        # Generate response with specific parameters
        response = model.generate_content(
            full_prompt,
            generation_config={
                'temperature': 0.7,  # Balance between creativity and consistency
                'top_p': 0.8,        # Nucleus sampling parameter
                'top_k': 40,         # Limit vocabulary diversity
                'max_output_tokens': 500  # Reasonable response length
            }
        )
        
        if response and hasattr(response, "text"):
            # Process the response to ensure it's specific
            processed_response = response.text.strip()
            
            # Verify if response is plant-related
            # if not any(keyword in processed_response.lower() for keyword in 
            #           ['plant', 'garden', 'soil', 'water', 'grow', 'leaf', 'root']):
            #     return "Please ask only plant-related questions!"
                
            return processed_response
            
        return "I apologize, but I couldn't generate a specific response. Please try rephrasing your question."
    
    except Exception as e:
        return f"An error occurred: {str(e)}. Please try again with a different question."


@dashboard_bp.route('/chatbot_toggle', methods=['POST'])
@login_required
def chatbot_toggle():
    chat_session.is_open = not chat_session.is_open
    return redirect(url_for('dashboard.dashboard'))





@dashboard_bp.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    user_message = request.form.get("message", "").strip()
    
    if not user_message:
        return redirect(url_for('dashboard.dashboard'))
    
    # Add user message to history
    chat_session.add_message("User", user_message)
    
    # Generate and add bot response
    response = chatbot_response(user_message, chat_session.chat_history)
    chat_session.add_message("Plantie 🌼", response)
    
    return redirect(url_for('dashboard.dashboard'))



@dashboard_bp.route('/admin', methods=['GET', 'POST'], endpoint='admin_dashboard')
@role_required('admin')  # Restrict access to admins only
def admin_dashboard():
    return render_template('dashboard_admin.html')

