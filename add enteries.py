import pandas as pd
import pymysql

# Connect to the database
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="Vidhi@3112",
    database="gardening_companion"
)

cursor = connection.cursor()

# Read the Excel file
file_path = "/home/vidhi/Downloads/final.xlsx"
data = pd.read_excel(file_path)

# Rename columns to match the database schema
data.rename(columns={
    "Common Name": "CommonName",
    "Scientific Name": "ScientificName",
    "Year": "Year",
    "Author": "Author",
    "Status": "Status",
    "Rank": "Rank",
    "Family Common Name": "FamilyCommonName",
    "Genus": "Genus",
    "Image URL": "ImageURL",
    "Edible": "Edible",
    "Sapling Description": "SaplingDescription"
}, inplace=True)

# Handle NaN values (replace NaN with None)
data = data.replace({pd.NA: None, pd.NaT: None, float("nan"): None})

# Insert data into the database
for _, row in data.iterrows():
    cursor.execute("""
        INSERT INTO PlantInfo (CommonName, ScientificName, `Year`, Author, Status, `Rank`, FamilyCommonName, Genus, ImageURL, Edible, SaplingDescription)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row['CommonName'],
        row['ScientificName'],
        row['Year'],
        row['Author'],
        row['Status'],
        row['Rank'],
        row['FamilyCommonName'],
        row['Genus'],
        row['ImageURL'],
        row['Edible'],
        row['SaplingDescription']
    ))

# Commit changes and close the connection
connection.commit()
cursor.close()
connection.close()
