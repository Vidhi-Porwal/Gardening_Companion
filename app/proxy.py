import requests

@app.route('/api/generate', methods=['POST'])
def generate_response():
    user_input = request.json.get('input')
    proxies = {
        'http': 'http://your_proxy_ip:port',
        'https': 'http://your_proxy_ip:port',
    }
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    
    # Use requests with proxy settings if necessary (for external calls)
    response = chat.send_message(user_input, proxies=proxies)
    
    return jsonify({'response': response.text})
