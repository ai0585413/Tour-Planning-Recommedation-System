from flask import Blueprint, render_template
import mysql.connector
import re

map_app = Blueprint("map_app", __name__)

# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'dd',
}
def get_routes():
    """Fetch the latest routes and their coordinates from the database."""
    try:
        conn = mysql.connector.connect(**db_config)
        place_coordinates = []

        # Fetch the latest routes
        try:
            with conn.cursor(dictionary=True, buffered=True) as cursor:
                cursor.execute("""
                    SELECT map_route 
                    FROM map
                    ORDER BY id DESC 
                    LIMIT 3
                """)
                routes = cursor.fetchall()

            # Extract unique place names from map_route
            all_places = []
            for route in routes:
                places = route['map_route'].split('->')
                for place in places:
                    cleaned_place = re.sub(r'\d+:\s*', '', place).strip()
                    if cleaned_place and cleaned_place not in all_places:
                        all_places.append(cleaned_place)

            # Fetch coordinates for each place
            for place in all_places:
                with conn.cursor(dictionary=True, buffered=True) as cursor:
                    cursor.execute("""
                        SELECT title, longitude, latitude
                        FROM dataset
                        WHERE title = %s
                    """, (place,))
                    result = cursor.fetchone()
                    if result:
                        print(f"Fetched data for {place}: {result}")
                        place_coordinates.append({
                            'place': result['title'],
                            'longitude': result['longitude'],
                            'latitude': result['latitude']
                        })
        finally:
            if conn.is_connected():
                conn.close()  # Ensure the connection is closed

        return place_coordinates

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return []





@map_app.route("/")
def map_view():
    """Render the map view with routes."""
    routes = get_routes()
    return render_template('map.html', routes=routes)

