from app import create_app


from flask import Flask, request
from flask_mail import Mail, Message
from app.config import Config
from app.tasks import send_async_email
app = create_app()

@app.after_request
def add_header(response):
    # Disable caching of protected pages
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# print(app.url_map)


app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    subject = data.get('subject')
    recipients = data.get('recipients')
    body = data.get('body')

    send_async_email.delay(subject, recipients, body)

    return {'message': 'Email is being sent!'}, 202


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
