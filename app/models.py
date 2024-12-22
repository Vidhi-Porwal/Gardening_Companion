from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash


class User(UserMixin):
    def __init__(self, id, full_name, username, email, password_hash, phone_no, status):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.phone_no = phone_no
        self.status = status

    @staticmethod
    def get_user_by_id(user_id):
        connection = current_app.config['DB_CONNECTION']()
        try:
            with connection.cursor() as cursor:
                query = "SELECT * FROM users WHERE id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                if result:
                    return User(**result)
        finally:
            connection.close()
        return None

    @staticmethod
    def get_user_by_email(email):
        connection = current_app.config['DB_CONNECTION']()
        try:
            with connection.cursor() as cursor:
                query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                if result:
                    return User(**result)
        finally:
            connection.close()
        return None


    @staticmethod
    def create_user(full_name, username, email, password, phone_no):
        # Hash the password
        password_hash = generate_password_hash(password)

        # Get database connection
        connection = current_app.config['DB_CONNECTION']()

        try:
            with connection.cursor() as cursor:
                # Insert user into the database
                query = """
                INSERT INTO users (full_name, username, email, password_hash, phone_no, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (full_name, username, email, password, phone_no, 'active'))
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def get_user_by_username_or_phone(identifier):
        connection = current_app.config['DB_CONNECTION']()
        try:
            with connection.cursor() as cursor:
                query = """
                SELECT id, username, phone_no, full_name, email, password_hash, status
                FROM users 
                WHERE username = %s OR phone_no = %s
                """
                cursor.execute(query, (identifier, identifier))
                result = cursor.fetchone()
                if result:
                    # Ensure all required fields are mapped
                    return User(
                        id=result['id'],
                        username=result['username'],
                        phone_no=result['phone_no'],
                        full_name=result['full_name'],
                        email=result['email'],
                        password_hash=result['password_hash'],
                        status=result['status']
                    )
        finally:
            connection.close()
        return None

