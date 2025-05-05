# import pymongo
# import pandas as pd
# from urllib.parse import quote_plus
# #hello
# # Encode username & password
# username = "admin"
# password = "Gurpreet@23"  # Keep it empty if there's no password

# encoded_username = quote_plus(username)
# encoded_password = quote_plus(password)

# # Correct MongoDB Connection URI
# MONGO_URI = f"mongodb://{encoded_username}:{encoded_password}@3.86.209.148:27017/Gardening_Companion?authSource=admin"
# mongo_client = pymongo.MongoClient(MONGO_URI)

# db = mongo_client["Gardening_Companion"]
# collection = db["plants"]

# # Read the Excel file
# def read_excel_file(file_path):
#     try:
#         data = pd.read_excel(file_path)
#         return data
#     except Exception as e:
#         print(f"❌ Failed to read Excel file: {e}")
#         return None

# # Insert data into MongoDB
# def insert_data_into_mongodb(data):
#     try:
#         for index, row in data.iterrows():
#             # ✅ Ensure Image URL is stored as string only
#             imageURL = row.get('Image URL', '')  # Default to empty string if missing

#             if not isinstance(imageURL, str):
#                 imageURL = ''  # ✅ Convert NaN/float to empty string

#             document = {
#                 "commonName": row.get('Common Name', ''),
#                 "scientificName": row.get('Scientific Name', ''),
#                 "familyCommonName": row.get('Family Common Name', ''),
#                 "edible": row.get('Edible', ''),
#                 "saplingDescription": row.get('Sapling Description', ''),
#                 "genus": row.get('Genus', ''),
#                 "imageURL": imageURL,
#                 "rank":row.get('Rank',''),  # ✅ Store Image URL as string
#             }
#             collection.insert_one(document)
#         print("✅ Data inserted successfully!")
#     except Exception as e:
#         print(f"❌ Failed to insert data into MongoDB: {e}")

# # Main function
# def main():
#     file_path = "/home/gurpreet/Downloads/final.xlsx"  # Replace with your Excel file path
#     data = read_excel_file(file_path)
#     if data is not None:
#         insert_data_into_mongodb(data)

# if __name__ == "__main__":
#     main()

import pymongo
from urllib.parse import quote_plus

# Plant batch data
plants_batch_1 = [
    {
        "Common Name": "Jade Plant",
        "Scientific Name": "Crassula ovata",
        "Family Common Name": "Stonecrop family",
        "Edible": "False",
        "Genus": "Crassula",
        "Image URL": "https://upload.wikimedia.org/wikipedia/commons/5/58/Crassula_ovata_01.jpg",
        "Rank": "Species",
        "Sapling Description": """### SAPLING DESCRIPTION:
- **Number of saplings in a net pot** - 3-5 saplings
- **Sapling Height** - 4-6 inches
- **Watering** - Water when top soil is dry
- **Sunlight** - Bright indirect light

### PLANT DESCRIPTION:
- **Difficulty Level** - Moderate
- **Full Height** - 2-4 feet
- **Leaves Color** - Glossy green
- **Type** - Succulent
- **Feed** - Balanced fertilizer every 4-6 weeks
- **Soil** - Well-draining mix
- **Sunlight** - Bright light with some direct sun
- **Temperature** - 65-75°F (18-24°C)
"""
    }
    # Add more plant dictionaries if needed
    
]

# MongoDB credentials and connection
username = "admin"
password = "Gurpreet@23"  # Leave as "" if there's no password
host = "3.86.209.148"  # Replace with your MongoDB host or IP
port = "27017"  # Default port

# Encode credentials
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

MONGO_URI = f"mongodb://{encoded_username}:{encoded_password}@3.86.209.148:27017/Gardening_Companion?authSource=admin"

# Connect to MongoDB
try:
    mongo_client = pymongo.MongoClient(MONGO_URI)
    db = mongo_client["Gardening_Companion"]
    collection = db["plants"]
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    exit()

# Insert batch data into MongoDB
def insert_batch_data(data_list):
    try:
        for item in data_list:
            edible_value = item.get("Edible", "").strip().lower()
            edible_bool = True if edible_value == "true" else False

            document = {
                "commonName": item.get("Common Name", ""),
                "scientificName": item.get("Scientific Name", ""),
                "familyCommonName": item.get("Family Common Name", ""),
                "edible": edible_bool,
                "saplingDescription": item.get("Sapling Description", ""),
                "genus": item.get("Genus", ""),
                "imageURL": item.get("Image URL", "") if isinstance(item.get("Image URL"), str) else "",
                "rank": item.get("Rank", "")
            }
            collection.insert_one(document)
        print("✅ Batch data inserted successfully!")
    except Exception as e:
        print(f"❌ Failed to insert batch data: {e}")

# Main function
def main():
    insert_batch_data(plants_batch_1)

if __name__ == "__main__":
    main()
