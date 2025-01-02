from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user

from .models import User, UserPlant, PlantInfo
import google.generativeai as genai
import os

dashboard_bp = Blueprint('dashboard', __name__)

# Configure the Gemini API
api_key = os.getenv("GENAI_API_KEY", "AIzaSyCLCHIqeaIAHUXRrWLsgDTfftziD9BCqO0")  # Use environment variable for API key
genai.configure(api_key=api_key)


@dashboard_bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        # Fetch user plants and all plants
        user_plants = UserPlant.get_user_plants(current_user.id)
        plants = PlantInfo.get_all_plants()
        print(user_plants)
        # Generate content using Gemini API
        gemini_response = None
        


        if request.method == 'POST':
            # Handle adding a plant
            if 'add_plant' in request.form:
                plant_id = request.form.get('plant_id')
                if plant_id:
                    try:
                        plant_common_name = UserPlant.get_common_name(plant_id)
                        # with get_db_connection() as connection:
                        #     with connection.cursor() as cursor:
                        #         cursor.execute("SELECT common_name FROM PlantInfo WHERE id = %s", (plant_id,))
                        #         result = cursor.fetchone()
                        #         if result:
                        #             plant_common_name = result[0]
                        #         else:
                        #             print(f"No plant found with ID {plant_id}")
                        #             return "Plant not found", 404

                    # Generate the prompt dynamically
                        
                        # updated 
                    
                        
                        
                        
                        model = genai.GenerativeModel("gemini-1.5-flash")

                        response = model.generate_content( f"give me watering and fertilizing schedule for {plant_common_name}, "
                            "i just want number like in how many days return only a number, also give me amount of sunlight it need, "
                            "give me answer in no. 1 if full sunlight, 2 if partial sunlight, 3 if no sunlight, "
                            "also give me type of fertilizer recommended for this plant. "
                            "In watering and fertilizing give only a number, not like 2-3, give only 2 or only 3.")
                        gemini_response = response.text
                        print(gemini_response)
                    except Exception as e:
                        print(f"Error generating content: {e}")
                        gemini_response = "Error generating garden plant list."
                        # Add the plant to the user's garden
                    data = {}
                    for line in gemini_response.split("\n"):
                        if "Watering:" in line:
                            value = line.split(":")[1].strip()
                            data['watering'] = int(value) if value.isdigit() else None
                            
                        elif "Fertilizing:" in line:
                            value = line.split(":")[1].strip()
                            data['fertilizing'] = int(value) if value.isdigit() else None
                        elif "Sunlight:" in line:
                            value = line.split(":")[1].strip()
                            data['sunlight'] = int(value) if value.isdigit() else None
                        elif "Fertilizer type:" in line:
                            data['fertilizer_type'] = line.split(":")[1].strip() or "Unknown"

                    # Debugging the parsed data
                    print("Parsed Data:", data)
                
                    UserPlant.add_plant_to_user(current_user.id, plant_id,data['watering'],data['fertilizing'],
                            data['sunlight'],
                            data['fertilizer_type'],quantity=1)
                    print("user plant added")
                

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

            if 'show_plant' in request.form:
                plant_id = request.form.get('plant_id')
                if plant_id:
                    result = PlantInfo.get_plant_by_id(plant_id)
                    if not result:
                        print("Plant not displayed")
                    else:
                        print("Plant displayed")
                    return redirect(url_for('dashboard.dashboard'),result = result, plant_id = plant_id)

        # Render the dashboard page with all relevant data
        return render_template('dashboard.html', user_plants=user_plants, plants=plants, gemini_response=gemini_response, chatbot_open=chatbot_open, chat_history=chat_history)

    except Exception as e:
        print(f"Error in dashboard: {e}")
        return render_template('error.html', error_message="Something went wrong. Please try again later."), 500


# genai.configure(api_key="AIzaSyCF9pTtirypeeHUMTohJiepKntkuuP07hI")
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



@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html')























# @dashboard_bp.route('/', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     try:
#         # Fetch user plants and all plants
#         user_plants = UserPlant.get_user_plants(current_user.id)
#         plants = PlantInfo.get_all_plants()

#         # Generate content using Gemini API
#         gemini_response = None
#         try:
#             model = genai.GenerativeModel("gemini-1.5-flash")
#             response = model.generate_content("give me list of 100 indian common garden plants")
#             # print(response.text)
#             gemini_response = response.text
#         except Exception as e:
#             print(f"Error generating content: {e}")
#             gemini_response = "Error generating garden plant list."

#         # if request.method == 'POST':
#         #     # Handle adding a plant
#         #     if 'add_plant' in request.form:
#         #         plant_id = request.form.get('plant_id')
#         #         if plant_id:
#         #             UserPlant.add_plant_to_user(current_user.id, plant_id, quantity=1)

#         #             user_details = UserPlant.get_user_by_id(current_user.id)
#         #             numbers = user_details.phone_no
#         #             message_body = request.json.get('message', 'CONGRATS! NEW PLANT ADDED YOUR GARDEN')

#         #             responses = []
#         #             for number in numbers:
#         #                 response = send_whatsapp_message(number, message_body)
#         #                 responses.append({'number': number, 'response': response})
                    
#         #             return jsonify(responses)
#         #         return redirect(url_for('dashboard.dashboard'))

#         if 'add_plant' in request.form:
#             plant_id = request.form.get('plant_id')
#             if plant_id:
#                 # Add the plant to the user's list
#                 UserPlant.add_plant_to_user(current_user.id, plant_id, quantity=1)
#                 print("000000000000000000")
#                 # Fetch user details (assuming it returns a single user object, not a list)
#                 user_details = UserPlant.get_user_by_id(current_user.id)
#                 print("1111111111111111111")
#                 print (user_details)
#                 # Ensure user_details and phone_no are valid
#                 if user_details and user_details.phone_no:
#                     numbers = [user_details.phone_no]  # Ensure this is a list
#                     message_body = request.form.get(
#                         'message', 'CONGRATS! NEW PLANT ADDED TO YOUR GARDEN'
#                     )

#                     responses = []
#                     for number in numbers:
#                         response = send_whatsapp_message(number, message_body)
#                         responses.append({'number': number, 'response': response})

#                     return jsonify(responses)

#         # Handle removing a plant
#         if 'remove_plant' in request.form:
#             plant_id = request.form.get('plant_id')
#             print(f"Removing plant with ID: {plant_id}")  # Debug log
#             if plant_id:
#                 success = UserPlant.remove_plant_from_user(current_user.id, plant_id)
#                 if not success:
#                     print("Plant not removed")
#                 else:
#                     print("Plant removed successfully")
#             return redirect(url_for('dashboard.dashboard'))

#         return render_template('dashboard.html', user_plants=user_plants, plants=plants, gemini_response=gemini_response)
#     except Exception as e:
#         print(f"Error in dashboard: {e}")
#         return render_template('error.html', error_message="Something went wrong. Please try again later."), 500

# # Function to send a WhatsApp message
# def send_whatsapp_message(to_number, message_body):
#     try:
#         client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#         message = client.messages.create(
#             body=message_body,
#             from_=TWILIO_WHATSAPP_NUMBER,
#             to=f"whatsapp:{to_number}"
#         )
#         return f"Message sent: SID {message.sid}"
#     except Exception as e:
#         return f"Failed to send message: {e}"
