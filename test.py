import google.generativeai as genai

# Configure the Generative AI API
genai.configure(api_key="AIzaSyCF9pTtirypeeHUMTohJiepKntkuuP07hI")
model = genai.GenerativeModel("gemini-1.5-flash")

# Helper function for general question-answering with a cute and exciting tone
def chatbot_response(prompt, chat_history=[]):
    if chat_history:
        prompt = "\n".join(chat_history) + "\n" + prompt

    # Prepend a directive to encourage concise responses
    concise_prompt = f"Please answer briefly: {prompt}"

    # Generate the response from the model
    try:
        response = model.generate_content(concise_prompt)
        
        # Check if the response contains valid text
        if response and hasattr(response, 'text') and response.text:
            # Modify the response to add a cute and exciting tone
            cute_response = f"🌟 {response.text} 🌼 Isn't that exciting? If you have more questions, just ask! 😊"
        else:
            cute_response = "Oops! I couldn't find the information you need. But I'm here to help! 🌼 What else would you like to know?"
    
    except Exception as e:
        cute_response = "Oh no! Something went wrong while trying to fetch the information. Please try again! 😊"

    chat_history.append(prompt)
    chat_history.append(cute_response)
    return cute_response, chat_history

# Example usage with real-time input for follow-ups
chat_history = []
introduction_displayed = False  # Flag to check if introduction has been displayed

while True:
    if not introduction_displayed:
        intro_message = "Hi! I am Plantie 🌻.  I love to talk about plants🌱 and share fun facts! ✨✨ Let's have a great time together!!! ✨🎉"
        print(f"Chatbot: {intro_message}")
        chat_history.append(intro_message)  # Add introduction to chat history
        introduction_displayed = True  # Set the flag to True

    user_input = input("You: ")  # Take user input dynamically
    if user_input.lower() in ["exit", "quit"]:  # Exit condition
        print("Chatbot: Goodbye! Have a great day! 🌈")
        break
    response, chat_history = chatbot_response(user_input, chat_history)
    # Modify the response to avoid referring to itself as "Plantie"
    response = response.replace("Plantie", "Buddy")  # Replace "Plantie" with "I"
    print(f"Chatbot: {response}")