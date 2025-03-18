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

    def __init__(self, full_name, id, username, email, phone_no=None, role='user'):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.email = email
        self.phone_no = phone_no
        self.role = role

    @staticmethod
    def find_by_identifier(db, identifier):
        """Find a user by username, email, or phone number."""
        return db.users.find_one({
            "$or": [
                {"username": identifier},
                {"email": identifier},
                {"phone_no": identifier}
            ]
        })

    @staticmethod
    def find_by_email(db, email):
        """Find a user by email."""
        return db.users.find_one({"email": email})

    @staticmethod
    def find_by_username(db, username):
        """Find a user by username."""
        return db.users.find_one({"username": username})

    @staticmethod
    def create_user(db, full_name, username, email, password, phone_no, role='user', status='active'):
        """Create a new user in the database."""
        hashed_password = generate_password_hash(password)
        user_data = {
            "full_name": full_name,
            "username": username,
            "email": email,
            "password_hash": hashed_password,
            "phone_no": phone_no,
            "role": role,
            "status": status
        }
        result = db.users.insert_one(user_data)
        return str(result.inserted_id)  # Return the new user's ID

    @staticmethod
    def check_password(user, password):
        """Check if the provided password matches the user's hashed password."""
        return check_password_hash(user['password_hash'], password)


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
