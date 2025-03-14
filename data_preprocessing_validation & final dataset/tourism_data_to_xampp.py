import json
import mysql.connector

# Load the JSON data from the file
with open('E:/class materials/1.Capstone A/json covertion final/tourismdatasetbd.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="",  # Replace with your MySQL password
    database="tourism_db"  # Replace with your database name
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS TourismDatasetBD (
    id INT PRIMARY KEY,
    upazila_name VARCHAR(255),
    search_key VARCHAR(255),
    title VARCHAR(255),
    address VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    category VARCHAR(255),
    rating FLOAT,
    ratingCount INT
)
''')

# Insert data into the table
for place in data:
    query = '''
    INSERT INTO TourismDatasetBD (id, upazila_name, search_key, title, address, latitude, longitude, category, rating, ratingCount)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    upazila_name=VALUES(upazila_name),
    search_key=VALUES(search_key),
    title=VALUES(title),
    address=VALUES(address),
    latitude=VALUES(latitude),
    longitude=VALUES(longitude),
    category=VALUES(category),
    rating=VALUES(rating),
    ratingCount=VALUES(ratingCount)
    '''
    values = (
        place['id'],
        place.get('upazila_name', ''),
        place.get('search_key', ''),
        place.get('title', ''),
        place.get('address', ''),
        place.get('latitude', 0.0),
        place.get('longitude', 0.0),
        place.get('category', ''),
        place.get('rating', 0),
        place.get('ratingCount', 0)
    )
    cursor.execute(query, values)

# Commit and close the connection
conn.commit()
cursor.close()
conn.close()

print("Data successfully saved to MySQL.")
