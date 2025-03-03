import json
import pymysql

# Database connection details
host = "localhost"
user = "root"
password = ""  # Replace with your MySQL password
database = "tourism_db"

# Establish connection to MySQL
connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
cursor = connection.cursor()

# Create table (if not exists)
create_table_query = """
CREATE TABLE IF NOT EXISTS places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position INT,
    title VARCHAR(255),
    address VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    thumbnailUrl TEXT,
    category VARCHAR(100),
    cid VARCHAR(50),
    upazila_name VARCHAR(100),
    search_key VARCHAR(100),
    rating FLOAT,
    ratingCount INT
);
"""
cursor.execute(create_table_query)

# Load JSON data
file_path = "merged_output.json"  # Replace with the actual file path if different
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Insert data into MySQL
insert_query = """
INSERT INTO places (
    position, title, address, latitude, longitude, thumbnailUrl, category, cid, upazila_name, search_key, rating, ratingCount
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

for entry in data:
    cursor.execute(insert_query, (
        entry.get("position"),
        entry.get("title"),
        entry.get("address"),
        entry.get("latitude"),
        entry.get("longitude"),
        entry.get("thumbnailUrl"),
        entry.get("category"),
        entry.get("cid"),
        entry.get("upazila_name"),
        entry.get("search_key"),
        entry.get("rating", None),  # Default to None if rating is not present
        entry.get("ratingCount", None)  # Default to None if ratingCount is not present
    ))

# Commit changes and close connection
connection.commit()
cursor.close()
connection.close()

print("Data successfully inserted into MySQL!")
