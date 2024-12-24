### models.py ###
from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

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
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
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
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                result = cursor.fetchone()
                if result:
                    return User(**result)
        finally:
            connection.close()
        return None

    @staticmethod
    def create_user(full_name, username, email, password, phone_no):
        password_hash = generate_password_hash(password)
        connection = current_app.config['DB_CONNECTION']()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (full_name, username, email, password_hash, phone_no, status)
                    VALUES (%s, %s, %s, %s, %s, 'active')
                    """,
                    (full_name, username, email, password_hash, phone_no)
                )
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def get_user_by_username_or_phone(identifier):
        connection = current_app.config['DB_CONNECTION']()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM users WHERE username = %s OR phone_no = %s
                    """,
                    (identifier, identifier)
                )
                result = cursor.fetchone()
                if result:
                    return User(**result)
        finally:
            connection.close()
        return None


class UserPlant:
    @staticmethod
    def get_user_plants(user_id):
        connection = current_app.config['DB_CONNECTION']()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.CommonName, p.ScientificName, up.quantity
                    FROM UserPlant up
                    JOIN PlantInfo p ON up.plant_id = p.ID
                    WHERE up.user_id = %s
                    """,
                    (user_id,)
                )
                return cursor.fetchall()
        finally:
            connection.close()

    @staticmethod
    def add_plant_to_user(user_id, plant_id, quantity):
        connection = current_app.config['DB_CONNECTION']()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO UserPlant (user_id, plant_id, quantity)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE quantity = quantity + %s
                    """,
                    (user_id, plant_id, quantity, quantity)
                )
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def remove_plant_from_user(user_id, plant_id):
        connection = current_app.config['DB_CONNECTION']()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM UserPlant WHERE user_id = %s AND plant_id = %s",
                    (user_id, plant_id)
                )
                connection.commit()
        finally:
            connection.close()