from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user

from .models import User, UserPlant, PlantInfo
import google.generativeai as genai
import os
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client


#twilio account setup
TWILIO_ACCOUNT_SID = "AC54864ecd02d827663926bf6d9a87fdc1"
TWILIO_AUTH_TOKEN = "e4b5e43443bcf2287cff9dabe4adbf7f"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+12185035494"


from .models import UserPlant, PlantInfo
import google.generativeai as genai
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

        # Generate content using Gemini API
        gemini_response = None
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content("give me a list of 100 Indian common garden plants")
            gemini_response = response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            gemini_response = "Error generating garden plant list."

        if request.method == 'POST':
            # Handle adding a plant
            if 'add_plant' in request.form:
                plant_id = request.form.get('plant_id')
                if plant_id:
                    # Add the plant to the user's garden
                    UserPlant.add_plant_to_user(current_user.id, plant_id, quantity=1)

                    # Fetch user details and send a message
                    user_details = User.get_user_by_id(current_user.id)
                    if user_details and user_details.phone_no:
                        numbers = [user_details.phone_no]
                        message_body = request.form.get('message', 'CONGRATS! NEW PLANT ADDED TO YOUR GARDEN')

                        responses = []
                        for number in numbers:
                            response = send_whatsapp_message(number, message_body)
                            responses.append({'number': number, 'response': response})

                        return jsonify(responses)  # Respond with WhatsApp message status

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

        # Render the dashboard page with all relevant data
        return render_template('dashboard.html', user_plants=user_plants, plants=plants, gemini_response=gemini_response)

    except Exception as e:
        print(f"Error in dashboard: {e}")
        return render_template('error.html', error_message="Something went wrong. Please try again later."), 500

# Function to send a WhatsApp message
def send_whatsapp_message(to_number, message_body):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{to_number}"
        )
        return f"Message sent: SID {message.sid}"
    except Exception as e:
        return f"Failed to send message: {e}"

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
