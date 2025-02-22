from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import google.generativeai as genai
from functools import wraps
import os
from bson.objectid import ObjectId
from .models import User
from datetime import datetime
from flask import render_template, request, jsonify
from pymongo import MongoClient


# Initialize blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Configure the Gemini API

api_key = os.getenv("GENAI_API_KEY", "AIzaSyAgiXHaX1IuWDErnEwfXdYRWMGhKUCehs0")  # Use environment variable for API key
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
                return redirect(url_for("auth.login"))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def ensure_default_garden(user_id):
    db = current_app.config['DB_CONNECTION']
    default_garden = db.garden.find_one({"user_id": ObjectId(user_id), "gardenName": "My Garden"})
    if not default_garden:
        db.garden.insert_one({
            "gardenName": "My Garden",
            "user_id": ObjectId(user_id)
        })


# Dashboard Route
@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
# @role_required('user')
def dashboard():
    try:
        # Access the MongoDB database
        db = current_app.config['DB_CONNECTION']
        garden_id = request.args.get("garden_id")
        # Fetch user's plants and all available plants
        print(garden_id,"garden id ")
        user_plants = list(db.garden_plant.find({"user_id": current_user.id,"garden_id":garden_id}))
        user_plants_data = list(db.garden_plant.find({"user_id": current_user.id}, {"plant_id": 1, "_id": 0}))
        
        id_current_user=ObjectId(current_user.id)
        
        user_garden = list(db.garden.find({"user_id": id_current_user},{"gardenName": 1}))
        # Extract plant IDs into a list
        plant_ids = [entry["plant_id"] for entry in user_plants_data]
        print("user garden",user_garden)
        # Fetch full plant details from plants collection
        user_plants = list(db.plants.find({"_id": {"$in": plant_ids}}))
        plants = list(db.plants.find())
         
        user = db.users.find_one({"_id": ObjectId(current_user.id)}, {"role": 1, "_id": 0})
        # print(user["role"])
        print(user)
        user_role=user["role"]
       

        gemini_response = None

        # Handle POST requests
        if request.method == 'POST':
            # Add a plant to the user's garden
            if 'add_plant' in request.form:
                plant_id = request.form.get('plant_id')
                print("plant_id", plant_id)
                plant_id = ObjectId(plant_id)

                if plant_id:
                    try:
                        # Fetch plant information from the database
                        plant_info = db.plants.find_one({"_id": plant_id})
                        print("Plant Info:", plant_info)

                        if not plant_info:
                            flash("Plant not found in the database.", "warning")
                            return redirect(url_for('dashboard.dashboard'))

                        plant_common_name = plant_info.get("commonName", "Unknown")

                        # Check if scheduling information already exists in the plant database
                        if all(key in plant_info for key in ["watering", "fertilizing", "sunlight", "fertilizer_type"]):
                            data = {
                                "watering": plant_info["watering"],
                                "fertilizing": plant_info["fertilizing"],
                                "sunlight": plant_info["sunlight"],
                                "fertilizer_type": plant_info["fertilizer_type"]
                            }
                            print("Using existing plant data:", data)
                        else:
                            # Fetch scheduling details from Gemini API
                            model = genai.GenerativeModel("gemini-1.5-flash")
                            print(plant_common_name)
                            
                            prompt = (f"Give me watering and fertilizing schedule for {plant_common_name}, "
                                    "I just want numbers like in how many days return only a number, "
                                    "also give me the amount of sunlight it needs. In sunlight, give: "
                                    "1 for full sunlight, 2 for partial sunlight, 3 for no sunlight. "
                                    "Also give me the type of fertilizer recommended. in watering and fertilizing also only give a number in output not a interval")
                            
                            response = model.generate_content(prompt)
                            gemini_response = response.text
                            print("Gemini Response:", gemini_response)

                            # Parse and store the response
                            data = parse_gemini_response(gemini_response)
                            
                            if data:
                                # Update the plant document with scheduling details
                                db.plants.update_one(
                                    {"_id": plant_id},
                                    {"$set": {
                                        "watering": data["watering"],
                                        "fertilizing": data["fertilizing"],
                                        "sunlight": data["sunlight"],
                                        "fertilizer_type": data["fertilizer_type"]
                                    }}
                                )
                                print("Updated plant with new scheduling data")

                        # Insert into garden_plant collection
                        db.garden_plant.insert_one({
                            "user_id": current_user.id,
                            "plant_id": plant_id,
                            "watering": data["watering"],
                            "fertilizing": data["fertilizing"],
                            "sunlight": data["sunlight"],
                            "fertilizer_type": data["fertilizer_type"],
                            "plant_common_name": plant_common_name
                        })

                        flash(f"{plant_common_name} has been added to your garden!", "success")

                    except Exception as e:
                        flash(f"Error adding plant: {str(e)}", "danger")

                return redirect(url_for('dashboard.dashboard'))


            # Remove a plant from the user's garden
            if 'remove_plant' in request.form:
                
                plant_id = request.form.get('plant_id')
                print("plant_id is ",plant_id)
                plant_id = ObjectId(plant_id)
                print("plant_id is ",plant_id)
                if plant_id:
                    result = db.garden_plant.delete_one({"user_id": current_user.id, "plant_id": plant_id})
                    if result.deleted_count == 0:
                        flash("Failed to remove plant.", "danger")
                    else:
                        flash("Plant removed successfully.", "success")
                    return redirect(url_for('dashboard.dashboard'))

        # Render the dashboard template
        return render_template('dashboard.html', user_plants=user_plants, user_plants_data=user_plants_data, plants=plants, gemini_response=gemini_response,  chatbot_open=chat_session.is_open,  # Updated to use chat_session
            chat_history=chat_session.chat_history, user_garden=user_garden,user_role=user_role)

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

    # Fetch the MongoDB connection from the current app context
    db = current_app.config['DB_CONNECTION']

    if garden_name and user_id:
        db.garden.insert_one({
            "gardenName": garden_name,
            "user_id": ObjectId(user_id),
            "created_at": datetime.now()
        })
        flash("Garden added successfully!")
    return redirect(url_for("dashboard.dashboard"))

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
    print("Chatbot state:", chat_session.is_open)
    print("00000000000000")
    return redirect(url_for('dashboard.dashboard')) 

@dashboard_bp.route('/hey', methods=['POST'])
def hey():
    return redirect('dashboard.dashboard')


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


# @dashboard_bp.route('/admin', methods=['GET', 'POST'], endpoint='admin_dashboard')
# @role_required('admin')  # Restrict access to admins only
# def admin_dashboard():
#     return render_template('dashboard_admin.html')

# Route to render admin dashboard
@dashboard_bp.route("/admin", methods=["POST"])
def admin_dashboard():
    db = current_app.config['DB_CONNECTION']
    users = list(db.users.find({}, {"_id": 1, "full_name": 1, "username": 1, "email": 1, "phone_no": 1, "status": 1, "role": 1}))
    plants = list(db.plants.find({}, {"_id": 1, "commonName": 1, "scientificName": 1, "familyCommonName": 1, "edible": 1,"genus":1,"imageURL":1}))
    return render_template("admin.html", users=users, plants=plants)


# @dashboard_bp.route("/add_plant", methods=["POST"])
# def add_plant():
#     data = request.json
#     plant = {
#         "common_name": data["common_name"],
#         "scientific_name": data["scientific_name"],
#         "family_common_name": data.get("family_common_name", ""),
#         "year": data.get("year", ""),
#         "author": data.get("author", ""),
#         "image_url": data.get("image_url", ""),
#         "edible": int(data.get("edible", 0)),
#         "description": data.get("description", ""),
#     }
#     db.plants.insert_one(plant)
#     return jsonify({"message": "Plant added successfully!"}), 201


# from flask import Blueprint, jsonify, request
# from bson import ObjectId

# dashboard_bp = Blueprint("dashboard", __name__)

# # Delete a plant
@dashboard_bp.route("/delete_plant/<plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    db = current_app.config['DB_CONNECTION']
    print("Deleting plant:", plant_id)
    db.plants.delete_one({"_id": ObjectId(plant_id)})  # ✅ Fix: Convert to ObjectId
    print("Deleting plant:", plant_id)

    users = list(db.users.find({}, {"_id": 1, "full_name": 1, "username": 1, "email": 1, "phone_no": 1, "status": 1, "role": 1}))
    plants = list(db.plants.find({}, {"_id": 1, "commonName": 1, "scientificName": 1, "familyCommonName": 1, "edible": 1,"genus":1,"imageURL":1})) # ✅ Fix: Convert to ObjectId
    return jsonify({"message": "plant deleted successfully!"})

# Delete a user
@dashboard_bp.route("/delete_user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    print("Deleting user:", user_id)
    db = current_app.config['DB_CONNECTION']
    db.users.delete_one({"_id": ObjectId(user_id)}) 
    print("Deleting user:", user_id)

    users = list(db.users.find({}, {"_id": 1, "full_name": 1, "username": 1, "email": 1, "phone_no": 1, "status": 1, "role": 1}))
    plants = list(db.plants.find({}, {"_id": 1, "commonName": 1, "scientificName": 1, "familyCommonName": 1, "edible": 1,"genus":1,"imageURL":1})) # ✅ Fix: Convert to ObjectId
    return jsonify({"message": "User deleted successfully!"})

# Update a user's role
@dashboard_bp.route("/update_user_role/<user_id>", methods=["PUT"])
def update_user_role(user_id):
    print("update")
    data = request.json
    new_role = data.get("role", "")
    print(new_role)
    db = current_app.config['DB_CONNECTION']
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role}})  # ✅ Fix: Convert to ObjectId
    return jsonify({"message": "User role updated successfully!"})



@dashboard_bp.route('/add_plant', methods=['POST'])
@login_required
def add_plant():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard.dashboard'))
    
    db = current_app.config['DB_CONNECTION']
    data = request.json
    new_plant = {
        "commonName": data.get('commonName'),
        "scientificName": data.get('scientificName'),
        "rank": data.get('rank'),
        "familyCommonName": data.get('familyCommonName'),
        "genus": data.get('genus'),
        "imageURL": data.get('imageURL'),
        "edible": data.get('edible', False),
        "saplingDescription": data.get('saplingDescription')
    }
    
    db.plants.insert_one(new_plant)  # MongoDB insertion
    return jsonify({"message": "Plant added successfully!"})

@dashboard_bp.route('/edit_plant/<plant_id>', methods=['PUT'])
@login_required
def edit_plant(plant_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    data = request.json
    db = current_app.config['DB_CONNECTION']
    update_data = {
        "commonName": data.get("commonName"),
        "scientificName": data.get("scientificName"),
        "rank": data.get("rank"),
        "familyCommonName": data.get("familyCommonName"),
        "genus": data.get("genus"),
        "imageURL": data.get("imageURL"),
        "edible": data.get("edible"),
        "saplingDescription": data.get("saplingDescription")
    }

    db.plants.update_one({"_id": ObjectId(plant_id)}, {"$set": update_data})
    return jsonify({"message": "Plant updated successfully!"})

@dashboard_bp.route("/get_plant/<plant_id>", methods=["GET"])
@login_required
def get_plant(plant_id):
    db = current_app.config['DB_CONNECTION']
    plant = db.plants.find_one({"_id": ObjectId(plant_id)})
    if not plant:
        return jsonify({"error": "Plant not found"}), 404

    plant["_id"] = str(plant["_id"])  # Convert ObjectId to string for JSON response
    return jsonify(plant)
