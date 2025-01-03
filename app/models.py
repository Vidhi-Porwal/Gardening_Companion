from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import logging
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.ERROR)

# Context manager for DB connections
@contextmanager
def get_db_connection():
    connection = current_app.config['DB_CONNECTION']()
    try:
        yield connection
    finally:
        connection.close()

# User model
class User(UserMixin):
    def __init__(self, id, full_name, username, email, password_hash, phone_no, status, **kwargs):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.phone_no = phone_no
        self.status = status

    @staticmethod
    def get_user_by_id(user_id):
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, full_name, username, email, password_hash, phone_no, status FROM users WHERE id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    return User(**result)
        return None

    @staticmethod
    def get_user_by_email(email):
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, full_name, username, email, password_hash, phone_no, status FROM users WHERE email = %s", (email,))
                result = cursor.fetchone()
                if result:
                    return User(**result)
        return None

    @staticmethod
    def create_user(full_name, username, email, password, phone_no):
        password_hash = generate_password_hash(password)
        with get_db_connection() as connection:
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
            except Exception as e:
                logging.error(f"Error creating user: {e}")
                connection.rollback()

    @staticmethod
    def get_user_by_username_or_phone(identifier):
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, full_name, username, email, password_hash, phone_no, status FROM users WHERE username = %s OR phone_no = %s
                    """,
                    (identifier, identifier)
                )
                result = cursor.fetchone()
                if result:
                    return User(**result)
        return None

    @staticmethod
    def update_user(user_id, full_name, username, email, phone_no):
        """
        Updates the user details in the database.

        Args:
            user_id (int): The ID of the user to update.
            full_name (str): The updated full name.
            username (str): The updated username.
            email (str): The updated email address.
            phone_no (str): The updated phone number.
        """
        with get_db_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE users
                        SET full_name = %s, username = %s, email = %s, phone_no = %s
                        WHERE id = %s
                        """,
                        (full_name, username, email, phone_no, user_id)
                    )
                    connection.commit()
                    logging.info(f"User with ID {user_id} updated successfully.")
            except Exception as e:
                logging.error(f"Error updating user with ID {user_id}: {e}")
                connection.rollback()
                raise



    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_status(self, new_status):
        if new_status in ['active', 'inactive', 'banned']:
            with get_db_connection() as connection:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE users SET status = %s WHERE id = %s", (new_status, self.id))
                        connection.commit()
                except Exception as e:
                    logging.error(f"Error updating status: {e}")
                    connection.rollback()


# UserPlant model
class UserPlant:
    @staticmethod
    def get_user_plants(user_id):
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT up.plant_id, p.CommonName, p.ScientificName, p.ImageURL,
                           up.quantity, p.FamilyCommonName, p.Genus, p.Edible, 
                           p.SaplingDescription, p.PlantDescription, p.Status, p.Rank,
                           up.watering,up.fertilizing,up.fertilizer_type,up.sunlight
                    FROM UserPlant up
                    JOIN PlantInfo p ON up.plant_id = p.ID
                    WHERE up.user_id = %s
                    """,
                    (user_id,)
                )
                return cursor.fetchall()


   
    @staticmethod
    def add_plant_to_user(user_id, plant_id, watering, fertilizing, sunlight, fertilizer_type, quantity):
        with get_db_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO UserPlant(user_id, plant_id, quantity, watering, fertilizing, sunlight, fertilizer_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE quantity = quantity + %s
                        """,
                        (user_id, plant_id, quantity, watering, fertilizing, sunlight, fertilizer_type, quantity)
                    )
                    connection.commit()
            except Exception as e:
                logging.error(f"Error adding plant to user: {e}")
                connection.rollback()

    @staticmethod            
    def get_common_name(plant_id):
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT CommonName FROM PlantInfo WHERE id = %s", (plant_id,))
                result = cursor.fetchone()
                if result:
                    return result
                else:
                    print(f"No plant found with ID {plant_id}")
                    return "Plant not found", 404

    @staticmethod
    def remove_plant_from_user(user_id, plant_id):
        with get_db_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    # Check if the plant exists
                    cursor.execute(
                        "SELECT 1 FROM UserPlant WHERE user_id = %s AND plant_id = %s",
                        (user_id, plant_id)
                    )
                    if not cursor.fetchone():
                        logging.warning(f"Plant not found for removal (user_id={user_id}, plant_id={plant_id})")
                        return False  # No record found
                    
                    # Perform deletion
                    cursor.execute(
                        "DELETE FROM UserPlant WHERE user_id = %s AND plant_id = %s",
                        (user_id, plant_id)
                    )
                    connection.commit()
                    return True
            except Exception as e:
                logging.error(f"Error removing plant from user: {e}")
                connection.rollback()
                return False


# PlantInfo model
class PlantInfo:
    @staticmethod
    def get_all_plants():
        with get_db_connection() as connection:
            # import pdb; pdb.set_trace();
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT ID, CommonName FROM PlantInfo")
                    results = cursor.fetchall()
                    return results
            except Exception as e:
                logging.error(f"Error fetching plants: {e}")
                return []

    @staticmethod
    def get_plant_by_id():
        with get_db_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM PlantInfo WHERE ID = %s")
                    result = cursor.fetchone()
                    return result
            except Exception as e:
                logging.error(f"Error fetching plants: {e}")
                return []