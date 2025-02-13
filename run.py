from app import create_app

app = create_app()
# from pymongo import MongoClient

# client = MongoClient("mongodb://3.86.209.148:27017/")  # Replace with your MongoDB URI
# db = client['Gardening_Companion']  # Replace 'your_database_name' with the actual DB name

# # Example: Store `db` in app context for use in the app
# @app.before_request
# def set_db():
#     app.config['db'] = db

if __name__ == '__main__':
    app.run(debug=True)

