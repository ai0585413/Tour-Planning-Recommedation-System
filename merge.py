import time
import mysql.connector
from collections import defaultdict, deque
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import math
import heapq
import itertools
import sys




merge_app = Blueprint('merge_app', __name__)









# Function to calculate Haversine distance between two coordinates
def haversine_distance(coord1, coord2):
    R = 6371  # Radius of the Earth in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon1 - lon2)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c



# Distance in kilometers


def filter_unique_ids(places):
    title_to_id = {}
    for place in places:
        place_id, place_name, title, place_coords = place
        if title not in title_to_id:
            title_to_id[title] = place_id
    return [place for place in places if place[0] in title_to_id.values()]


def get_filtered_places(start_coords, end_coords, places, tolerance=0.01, max_distance_km=None):
    route_filtered_places = []
    near_filtered_places = []
    start_to_end_distance = haversine_distance(start_coords, end_coords)

    for place in places:
        place_id, place_name, title, place_coords = place
        distance_to_start = haversine_distance(start_coords, place_coords)
        distance_to_end = haversine_distance(end_coords, place_coords)
        total_distance = distance_to_start + distance_to_end

        if abs(total_distance - start_to_end_distance) <= tolerance:
            route_filtered_places.append(
                (place_id, place_name, title, place_coords, distance_to_start, distance_to_end))

        if max_distance_km is not None and (distance_to_start <= max_distance_km or distance_to_end <= max_distance_km):
            near_filtered_places.append((place_id, place_name, title, place_coords, distance_to_start, distance_to_end))

    filtered_places = list({place[0]: place for place in route_filtered_places + near_filtered_places}.values())

    return filtered_places


def get_distance_between_places(place1, place2):
    # place1 and place2 are tuples of (latitude, longitude)
    return haversine_distance(place1, place2)


def fixed_distance_dijkstra_filtered_places(filtered_places, start_id, max_distance):
    place_dict = {place[0]: place for place in filtered_places}

    if start_id not in place_dict:
        raise ValueError("Start place not found in filtered places.")

    heap = [(0, start_id)]
    distances = {start_id: 0}
    visited = set()
    neighbors = []

    while heap:
        current_distance, current_id = heapq.heappop(heap)

        if current_id in visited:
            continue

        visited.add(current_id)

        if current_id != start_id:
            neighbors.append(place_dict[current_id])

        current_place = place_dict[current_id]
        current_coords = current_place[3]  # Extract coordinates

        for neighbor_id, neighbor in place_dict.items():
            if neighbor_id != current_id and neighbor_id not in visited:
                neighbor_coords = neighbor[3]  # Extract coordinates
                distance = get_distance_between_places(current_coords, neighbor_coords)

                if distance <= max_distance:
                    new_distance = current_distance + distance
                    if neighbor_id not in distances or new_distance < distances[neighbor_id]:
                        distances[neighbor_id] = new_distance
                        heapq.heappush(heap, (new_distance, neighbor_id))

    return neighbors
def process_in_batches(cursor, query, batch_size):
    cursor.execute(query)
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch


def find_nearest_neighbors(start_id, end_id, filtered_places, max_distance):
    coordinates_dict = {place[0]: place[3] for place in filtered_places}
    connections = []

    for place in filtered_places:
        place_id = place[0]
        if place_id != end_id:
            neighbors = fixed_distance_dijkstra_filtered_places(filtered_places, place_id, max_distance)
            connections.extend((place_id, neighbor[0]) for neighbor in neighbors if neighbor[0] != place_id)

    return connections, coordinates_dict


def create_graph_from_connections(connections, coordinates_dict):
    graph = defaultdict(set)
    for start, neighbor in connections:
        if start in coordinates_dict and neighbor in coordinates_dict:
            graph[start].add(neighbor)
            graph[neighbor].add(start)

    return graph


def find_all_paths(graph, start, end, path_limit=1000):
    paths = []
    queue = deque([(start, [start])])

    while queue and len(paths) < path_limit:
        node, path = queue.popleft()

        for neighbor in graph[node]:
            if neighbor not in path:
                new_path = path + [neighbor]
                if neighbor == end:
                    paths.append(new_path)
                else:
                    queue.append((neighbor, new_path))

                if len(queue) > 100000:
                    queue.clear()

    return paths


def fetch_ratings_and_counts(cursor, place_ids):
    ratings_and_counts = {}
    if not place_ids:
        return ratings_and_counts

    format_strings = ','.join(['%s'] * len(place_ids))
    query = f"SELECT id, rating, ratingCount FROM dataset WHERE id IN ({format_strings})"
    try:
        cursor.execute(query, tuple(place_ids))
        for place_id, rating, rating_count in cursor:
            ratings_and_counts[place_id] = (rating, rating_count)
    except mysql.connector.Error as err:
        print(f"SQL Error: {err}")
        print(f"Query: {query}")
        print(f"Parameters: {tuple(place_ids)}")

    return ratings_and_counts

@merge_app.route('/go-back')
def go_back():
    return redirect(request.referrer or '/')




def calculate_knapsack_score(paths, ratings_and_counts, coordinates_dict, time_in_hours, avg_speed_kmh):
    knapsack_scores = []
    valid_routes = []
    max_time_minutes = int(time_in_hours * 60)  # Convert time to minutes

    for formatted_path, path in paths:
        n = len(path) - 1
        if n == 0:  # Skip paths with no segments
            continue

        dp = [[0 for _ in range(max_time_minutes + 1)] for _ in range(n + 1)]
        segment_profits = []
        segment_times = []

        for i in range(n):
            place1 = path[i]
            place2 = path[i + 1]

            # Ensure coordinates are available for both places
            if place1 not in coordinates_dict or place2 not in coordinates_dict:
                continue

            # Calculate distance and time between segments
            segment_distance = get_distance_between_places(
                coordinates_dict[place1], coordinates_dict[place2]
            )
            segment_time_minutes = (segment_distance / avg_speed_kmh) * 60 + 40  # Add 40 mins buffer

            # Fetch ratings and counts, defaulting to 0 if missing
            rating1, count1 = ratings_and_counts.get(place1, (0, 0))
            rating2, count2 = ratings_and_counts.get(place2, (0, 0))

            # Ensure ratings and counts are not None
            rating1 = rating1 or 0
            rating2 = rating2 or 0
            count1 = count1 or 0
            count2 = count2 or 0

            # Log places with invalid ratings for debugging
            if rating1 == 0 or rating2 == 0:
                print(f"Invalid rating detected for places: {place1}, {place2}")

            # Compute average rating and counts for the segment
            avg_rating = (rating1 + rating2) / 2
            avg_count = (count1 + count2) / 2

            # Time penalty based on segment time
            time_penalty = segment_time_minutes / max_time_minutes

            # Calculate profit for the segment
            segment_profit = (avg_rating + avg_count) - time_penalty

            # Append calculated values
            segment_profits.append(segment_profit)
            segment_times.append(segment_time_minutes)

        # Knapsack DP logic to optimize score for total time
        for i in range(1, n + 1):
            for t in range(max_time_minutes + 1):
                if segment_times[i - 1] <= t:
                    include_profit = dp[i - 1][int(t - segment_times[i - 1])] + segment_profits[i - 1]
                    exclude_profit = dp[i - 1][t]
                    dp[i][t] = max(include_profit, exclude_profit)
                else:
                    dp[i][t] = dp[i - 1][t]

        # Optimal profit for the path
        optimal_profit = dp[n][max_time_minutes]

        # Total time for the route
        total_time_hours = sum(segment_times) / 60  # Convert to hours

        # Add to results
        knapsack_scores.append((formatted_path, optimal_profit, total_time_hours))

        # Check if this route is valid within a tolerance range
        tolerance = 1
        if time_in_hours - tolerance <= total_time_hours <= time_in_hours:
            valid_routes.append((formatted_path, optimal_profit, total_time_hours))

    # Sort results based on the profit
    knapsack_scores.sort(key=lambda x: x[1], reverse=True)
    valid_routes.sort(key=lambda x: x[1], reverse=True)

    return knapsack_scores, valid_routes

@merge_app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q')
    results = []
    if query:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="dd"
        )
        cursor = db.cursor()
        sql = "SELECT title FROM dataset WHERE title LIKE %s LIMIT 10"
        cursor.execute(sql, ('%' + query + '%',))
        results = [row[0] for row in cursor.fetchall()]
        cursor.close()
        db.close()
    return jsonify(results)



@merge_app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_time = time.time()

        # Database connection
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Enter your MySQL password here
            database="dd"  # Enter your database name here
        )

        cursor = db.cursor()

        try:
            time_in_hours = float(request.form['time_in_hours'])
            avg_speed_kmh = 50

            search_key = request.form['current_location'].strip().lower()
            end_key = request.form['end_location'].strip().lower()

            # Fetch the reference point based on the search key
            query = "SELECT id, latitude, longitude FROM dataset WHERE LOWER(TRIM(title)) = %s LIMIT 1"
            cursor.execute(query, (search_key,))
            reference_point = cursor.fetchone()

            if reference_point:
                reference_id, reference_lat, reference_lon = reference_point
            else:
                return "Search key not found in the dataset."

            # Fetch the end point based on the search key
            cursor.execute(query, (end_key,))
            end_point = cursor.fetchone()

            if end_point:
                end_id, end_lat, end_lon = end_point
            else:
                return "End location not found in the dataset."

            # Fetch the dataset in batches
            query = "SELECT id, place_name, title, latitude, longitude FROM dataset"
            batch_size = 1000
            places = []

            for batch in process_in_batches(cursor, query, batch_size):
                places.extend([(row[0], row[1], row[2], (row[3], row[4])) for row in batch])

            unique_filtered_places = filter_unique_ids(places)

            start_coords = (reference_lat, reference_lon)
            end_coords = (end_lat, end_lon)

            filtered_places = get_filtered_places(start_coords, end_coords, unique_filtered_places, tolerance=0.01, max_distance_km=10)

            all_places = [(place[0], place[1], place[2], place[3]) for place in filtered_places]

            max_distance = 50
            connections, coordinates_dict = find_nearest_neighbors(reference_id, end_id, filtered_places, max_distance)

            end_neighbors = fixed_distance_dijkstra_filtered_places(filtered_places, end_id, 130)
            connections.extend((end_id, neighbor[0]) for neighbor in end_neighbors if neighbor[0] != end_id)

            graph = create_graph_from_connections(connections, coordinates_dict)

            paths = find_all_paths(graph, reference_id, end_id)

            id_to_title = {place[0]: place[2] for place in filtered_places}

            all_paths_titles = []

            for i, path in enumerate(paths, 1):
                if len(path) >= 4:
                    path_titles = [id_to_title[place_id] for place_id in path]
                    formatted_path = f"{i}: {' -> '.join(path_titles)}"
                    all_paths_titles.append((formatted_path, path))

            all_place_ids = set(place_id for _, path in all_paths_titles for place_id in path)
            ratings_and_counts = fetch_ratings_and_counts(cursor, all_place_ids)

            knapsack_scores, valid_routes = calculate_knapsack_score(all_paths_titles, ratings_and_counts, coordinates_dict, time_in_hours, avg_speed_kmh)

            top_n = 3  # Change this to the number of top routes you want to display
            table_data = []

            for i, (formatted_path, score, travel_time) in enumerate(valid_routes[:top_n], start=1):
                map_file = f'/static/route_map_{i}.html'
                table_data.append({
                    "route_number": i,
                    "formatted_path": formatted_path,
                    "score": f"{score:.2f}",
                    "travel_time": f"{travel_time:.2f} hours",
                    "map_link": map_file  # Only the filename
                })

                # Define the query to check if the route already exists
                # Define the query to check if the route exists
                check_map_route_query = """
                    SELECT COUNT(*) FROM map WHERE map_route = %s
                """

                # Define the query to delete an existing route
                delete_map_route_query = """
                    DELETE FROM map WHERE map_route = %s
                """

                # Define the query to insert a new route
                insert_map_route_query = """
                    INSERT INTO map (map_route) VALUES (%s)
                """

                # Loop through each item in table_data and check if the route exists
                for route_data in table_data:
                    # Check if the route exists in the table
                    cursor.execute(check_map_route_query, (route_data['formatted_path'],))
                    result = cursor.fetchone()

                    # If the route exists (count is greater than 0), delete the existing route
                    if result[0] > 0:
                        cursor.execute(delete_map_route_query, (route_data['formatted_path'],))

                    # Insert the new route
                    cursor.execute(insert_map_route_query, (route_data['formatted_path'],))

                # Commit the transaction to save changes
                db.commit()

                # Save route recommendations for the user
                user_id = session.get('user_id')  # Get the logged-in user ID from the session
                if user_id:
                    # Prepare the insert query
                    save_query = """
                                INSERT INTO routes (user_id, start_location, end_location, duration, route)
                                VALUES (%s, %s, %s, %s, %s)
                            """

                    # Modify the check for duplicates to include user_id as well as the route
                    check_query = """
                                SELECT COUNT(*) FROM routes 
                                WHERE user_id = %s AND route = %s
                            """

                    for route_data in table_data:
                        # Check if the same user already has this route saved
                        cursor.execute(check_query, (user_id, route_data['formatted_path']))
                        count = cursor.fetchone()[0]

                        # If the count is zero, then insert the new route for this user
                        if count == 0:
                            cursor.execute(save_query, (
                                user_id, search_key, end_key, time_in_hours, route_data['formatted_path']
                            ))

                    # Commit the transaction to save changes
                    db.commit()

            return render_template('re.html', table_data=table_data)

        except mysql.connector.Error as err:
            return f"Error: {err}"

        finally:
            cursor.close()
            db.close()

        end_time = time.time()
        elapsed_time = end_time - start_time
        return f"Elapsed time: {elapsed_time:.2f} seconds"

    return render_template('Home.html')