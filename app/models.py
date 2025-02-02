from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from flask_login import UserMixin


# Set up logging
logging.basicConfig(level=logging.ERROR)

# MongoDB Helper
def get_db_collection(collection_name):
    """
    Helper function to get a MongoDB collection.
    """
    db = current_app.config['DB_CONNECTION']
    return db[collection_name]

# User Model
class User(UserMixin):
    def __init__(self, id=None, full_name=None, username=None, email=None, password_hash=None, phone_no=None, status=None, role=None, **kwargs):
        self.id = str(id)
        self.full_name = full_name
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.phone_no = phone_no
        self.status = status
        self.role = role

    def is_active(self):
        """Returns True if the user is active."""
        return self.status == 'active'

    def is_authenticated(self):
        """Returns True if the user is authenticated."""
        return True  # Flask-Login sets this to True when a user logs in.

    def is_anonymous(self):
        """Returns False since this is not an anonymous user."""
        return False

    def get_id(self):
        """Returns the user's ID as a string."""
        return str(self.id)

    @staticmethod
    def get_user_by_id(user_id):
        collection = get_db_collection("users")
        result = collection.find_one({"_id": user_id})
        return User(**result) if result else None

    @staticmethod
    def get_user_by_email(email):
        collection = get_db_collection("users")
        result = collection.find_one({"email": email})
        return User(**result) if result else None

    @staticmethod
    def create_user(full_name, username, email, password, phone_no):
        password_hash = generate_password_hash(password)
        collection = get_db_collection("users")
        try:
            user_data = {
                "full_name": full_name,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "phone_no": phone_no,
                "status": "active",
                "role": "client"
            }
            collection.insert_one(user_data)
        except Exception as e:
            logging.error(f"Error creating user: {e}")

    @staticmethod
    def update_user(user_id, full_name, username, email, phone_no):
        collection = get_db_collection("users")
        try:
            collection.update_one(
                {"_id": user_id},
                {"$set": {"full_name": full_name, "username": username, "email": email, "phone_no": phone_no}}
            )
            logging.info(f"User with ID {user_id} updated successfully.")
        except Exception as e:
            logging.error(f"Error updating user with ID {user_id}: {e}")
            raise

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_status(self, new_status):
        if new_status in ['active', 'inactive', 'banned']:
            collection = get_db_collection("users")
            try:
                collection.update_one({"_id": self.id}, {"$set": {"status": new_status}})
            except Exception as e:
                logging.error(f"Error updating status: {e}")

    @staticmethod
    def get_all_users():
        collection = get_db_collection("users")
        results = collection.find({})
        return [User(**result) for result in results]

# UserPlant Model
class UserPlant:
    @staticmethod
    def get_user_plants(user_id):
        collection = get_db_collection("user_plants")
        results = collection.find({"user_id": user_id})
        return list(results)

    @staticmethod
    def add_plant_to_user(user_id, plant_id, watering, fertilizing, sunlight, fertilizer_type, quantity):
        collection = get_db_collection("user_plants")
        try:
            collection.update_one(
                {"user_id": user_id, "plant_id": plant_id},
                {"$set": {
                    "watering": watering,
                    "fertilizing": fertilizing,
                    "sunlight": sunlight,
                    "fertilizer_type": fertilizer_type,
                }, "$inc": {"quantity": quantity}},
                upsert=True
            )
        except Exception as e:
            logging.error(f"Error adding plant to user: {e}")

    @staticmethod
    def get_common_name(plant_id):
        collection = get_db_collection("plants")
        result = collection.find_one({"_id": plant_id}, {"CommonName": 1})
        return result.get("CommonName") if result else None

    @staticmethod
    def remove_plant_from_user(user_id, plant_id):
        collection = get_db_collection("user_plants")
        try:
            result = collection.delete_one({"user_id": user_id, "plant_id": plant_id})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error removing plant from user: {e}")
            return False

# PlantInfo Model
class PlantInfo:
    @staticmethod
    def get_all_plants():
        collection = get_db_collection("plants")
        results = collection.find({}, {"_id": 1, "CommonName": 1, "ScientificName": 1})
        return list(results)

    @staticmethod
    def get_plant_by_id(plant_id):
        collection = get_db_collection("plants")
        result = collection.find_one({"_id": plant_id})
        return result
