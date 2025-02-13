import pymongo
import pandas as pd
import base64

# MongoDB connection details
mongo_client = pymongo.MongoClient("mongodb://3.86.209.148:27017")  # Change the URI if needed
db = mongo_client["Gardening_companions"]  # Replace with your database name
collection = db["plants1"]  # Replace with your collection name

# Read the Excel file
def read_excel_file(file_path):
    try:
        data = pd.read_excel(file_path)
        return data
    except Exception as e:
        print(f"Failed to read Excel file: {e}")
        return None

# Insert data into MongoDB
def insert_data_into_mongodb(data):
    try:
        for index, row in data.iterrows():
            # Convert the image URL to binary data
            imageURL = row['Image URL']  # Replace with the actual column name containing URLs
            binary_data = base64.b64encode(imageURL.encode('utf-8'))  # Convert URL to binary
            
            document = {
                
                "commonName": row['Common Name'],
                "scientificName": row['Scientific Name'],
                "familyCommonName":row['Family Common Name'],
                "edible":row['Edible'],
                
                
                "saplingDescription":row['Sapling Description'],
                "genus": row['Genus'],
                "imageURL": binary_data,  # Store the binary data
                # Add more fields as needed
            }
            collection.insert_one(document)
        print("Data inserted successfully!")
    except Exception as e:
        print(f"Failed to insert data into MongoDB: {e}")

# Main function
def main():
    file_path = "/home/gurpreet/Downloads/final.xlsx"  # Replace with your Excel file path
    data = read_excel_file(file_path)
    if data is not None:
        insert_data_into_mongodb(data)

if __name__ == "__main__":
    main()