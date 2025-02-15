from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_reset_token(email):
    """Generates a secure token for password reset."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt="password-reset-salt")

def verify_reset_token(token, expiration=3600):
    """Verifies the token and retrieves the email. Token expires after `expiration` seconds."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=expiration)
        return email
    except:
        return None  # Invalid or expired token
