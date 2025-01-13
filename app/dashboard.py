from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from .models import User, UserPlant, PlantInfo
import google.generativeai as genai
import os
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)

# Configure the Gemini API
api_key = os.getenv("GENAI_API_KEY", "AIzaSyCF9pTtirypeeHUMTohJiepKntkuuP07hI")  # Use environment variable for API key
genai.configure(api_key=api_key)

def role_required(role):
    """
    Decorator to restrict access to routes based on user roles.
    :param role: The required role (e.g., 'admin', 'client').
    """
    def decorator(func):
        @wraps(func)  # Preserve the original function name and docstring
        def wrapper(*args, **kwargs):
            # Check if the user is authenticated and has the required role
            if not current_user.is_authenticated:
                flash("You need to log in to access this page.", "warning")
                return redirect(url_for('auth.login'))  # Redirect to login page

            if current_user.role != role:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('dashboard.dashboard'))  # Redirect to user dashboard

            return func(*args, **kwargs)
        return wrapper
    return decorator

@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required('client')
def dashboard():
    try:
        # Fetch user plants and all plants
        user_plants = UserPlant.get_user_plants(current_user.id)
        plants = PlantInfo.get_all_plants()
        # print(user_plants)
        # Generate content using Gemini API
        gemini_response = None
        


        if request.method == 'POST':
            # Handle adding a plant
            if 'add_plant' in request.form:
                plant_id = request.form.get('plant_id')
                if plant_id:
                    try:
                        plant_common_name = UserPlant.get_common_name(plant_id)
                        model = genai.GenerativeModel("gemini-1.5-flash")

                        prompt = (f"Give me watering and fertilizing schedule for {plant_common_name}, "
                                  "i just want number like in how many days return only a number, "
                                  "also give me amount of sunlight it needs. In sunlight, give: "
                                  "1 for full sunlight, 2 for partial sunlight, 3 for no sunlight. "
                                  "Also give me the type of fertilizer recommended.")
                        response = model.generate_content(prompt)
                        gemini_response = response.text

                        data = parse_gemini_response(gemini_response)
                        if data:
                            UserPlant.add_plant_to_user(
                                current_user.id, plant_id, 
                                watering=data['watering'],
                                fertilizing=data['fertilizing'],
                                sunlight=data['sunlight'],
                                fertilizer_type=data['fertilizer_type']
                            )
                            flash(f"{plant_common_name} has been added to your garden!", "success")
                        else:
                            flash("Failed to parse plant care details.", "warning")
                    except Exception as e:
                        flash(f"Error adding plant: {str(e)}", "danger")

                # Insert into database
                
                return redirect(url_for('dashboard.dashboard'))


            # Handle removing a plant
            if 'remove_plant' in request.form:
                plant_id = request.form.get('plant_id')
                if plant_id:
                    success = UserPlant.remove_plant_from_user(current_user.id, plant_id)
                    if not success:
                        print("Plant not removed")
                    else:
                        print("Plant removed successfully")
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