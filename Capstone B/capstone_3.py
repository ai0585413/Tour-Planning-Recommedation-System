import time
import mysql.connector
from queue import PriorityQueue
from collections import defaultdict, deque
import math
import heapq
import itertools
import sys
import random

# Function to calculate Haversine distance between two coordinates
def haversine_distance(coord1, coord2):
    R = 6371  # Radius of the Earth in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon1 - lon2)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in kilometers


def filter_unique_ids(places):
    title_to_id = {}
    for place in places:
        place_id, place_name, title, place_coords = place
        if title not in title_to_id:
            title_to_id[title] = place_id
        # If a title is already in the dictionary, we skip adding it again to ensure uniqueness

    unique_ids = set(title_to_id.values())
    return [place for place in places if place[0] in unique_ids]


def get_filtered_places(start_coords, end_coords, places, tolerance=0.01, max_distance_km=None):
    route_filtered_places = []
    near_filtered_places = []
    start_to_end_distance = haversine_distance(start_coords, end_coords)

    for place in places:
        place_id, place_name, title, place_coords = place
        distance_to_start = haversine_distance(start_coords, place_coords)
        distance_to_end = haversine_distance(end_coords, place_coords)
        total_distance = distance_to_start + distance_to_end

        # Check if the place lies on the direct route
        if abs(total_distance - start_to_end_distance) <= tolerance:
            route_filtered_places.append(
                (place_id, place_name, title, place_coords, distance_to_start, distance_to_end))

        # Check if the place is within the max distance from start or end
        if max_distance_km is not None and (distance_to_start <= max_distance_km or distance_to_end <= max_distance_km):
            near_filtered_places.append((place_id, place_name, title, place_coords, distance_to_start, distance_to_end))

    # Combine the results, ensuring no duplicates
    filtered_places = list({place[0]: place for place in route_filtered_places + near_filtered_places}.values())

    return filtered_places


def create_graph(dataset):
    graph = defaultdict(list)
    for point1, point2 in itertools.combinations(dataset, 2):
        distance = haversine_distance(point1[3], point2[3])
        graph[point1[0]].append((point2[0], distance))
        graph[point2[0]].append((point1[0], distance))
    return graph


def fixed_distance_dijkstra(graph, start, max_distance):
    heap = [(0, start)]
    distances = {start: 0}
    visited = set()
    neighbors = []

    while heap:
        current_distance, current_point = heapq.heappop(heap)

        if current_point in visited:
            continue

        visited.add(current_point)
        if current_point != start:  # Exclude the starting point itself
            neighbors.append(current_point)

        for neighbor, weight in graph[current_point]:
            if neighbor not in visited:
                distance = current_distance + weight
                if distance <= max_distance:
                    if neighbor not in distances or distance < distances[neighbor]:
                        distances[neighbor] = distance
                        heapq.heappush(heap, (distance, neighbor))

    return neighbors


def process_in_batches(cursor, query, batch_size):
    cursor.execute(query)
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch


def find_nearest_neighbors(start_id, end_id, dataset, max_distance):
    graph = create_graph(dataset)
    coordinates_dict = {point[0]: point[3] for point in dataset}

    connections = []
    for point in dataset:
        neighbors = fixed_distance_dijkstra(graph, point[0], max_distance)

        if point[0] != end_id:
            connections.extend((point[0], neighbor) for neighbor in neighbors if neighbor != point[0])

    return connections, coordinates_dict


def create_graph_from_connections(connections, coordinates_dict):
    graph = defaultdict(list)
    added_edges = set()

    for start, neighbor in connections:
        if start in coordinates_dict and neighbor in coordinates_dict:
            edge = tuple(sorted((start, neighbor)))
            if edge not in added_edges:
                graph[start].append(neighbor)
                graph[neighbor].append(start)
                added_edges.add(edge)

    return graph


def find_all_paths(graph, start, end, path_limit=1000):
    paths = []
    queue = deque([(start, [start])])

    while queue and len(paths) < path_limit:
        (node, path) = queue.popleft()  # BFS uses popleft

        for neighbor in graph[node]:
            if neighbor not in path:
                new_path = path + [neighbor]
                if neighbor == end:
                    paths.append(new_path)
                else:
                    queue.append((neighbor, new_path))

                if len(queue) > 100000:
                    queue.clear()  # Clear queue if it gets too large to manage

    return paths


def calculate_path_distance(place1, place2, coordinates_dict):
    coord1 = coordinates_dict[place1]
    coord2 = coordinates_dict[place2]
    return haversine_distance(coord1, coord2)



def fetch_ratings_and_counts(cursor, place_ids):
    ratings_and_counts = {}
    format_strings = ','.join(['%s'] * len(place_ids))
    cursor.execute(f"SELECT id, rating, ratingCount FROM dataset WHERE id IN ({format_strings})", tuple(place_ids))

    for (place_id, rating, rating_count) in cursor:
        ratings_and_counts[place_id] = (rating, rating_count)

    return ratings_and_counts




def calculate_simulated_annealing(paths, ratings_and_counts, coordinates_dict, time_in_hours, avg_speed_kmh, initial_temperature=1000, cooling_rate=0.95, max_iterations=1000):
    knapsack_scores = []
    valid_routes = []

    for formatted_path, path in paths:
        n = len(path) - 1  # Number of segments in the path
        if n == 0:
            continue

        segment_profits = []
        segment_times = []

        for i in range(n):
            place1 = path[i]
            place2 = path[i + 1]

            segment_distance = calculate_path_distance(place1, place2, coordinates_dict)
            segment_time_minutes = (segment_distance / avg_speed_kmh) * 60
            rating1, count1 = ratings_and_counts.get(place1, (0, 0))
            rating2, count2 = ratings_and_counts.get(place2, (0, 0))

            avg_rating = (rating1 + rating2) / 2
            avg_count = (count1 + count2) / 2

            # Calculate profit as a combined measure of rating and count minus a time penalty
            time_penalty = segment_time_minutes / (time_in_hours * 60)  # Normalize time as a penalty
            segment_profit = (avg_rating + avg_count) - time_penalty

            segment_profits.append(segment_profit)
            segment_times.append(segment_time_minutes)

        # Simulated Annealing process
        current_solution = list(range(n))
        current_profit = sum(segment_profits[i] for i in current_solution)
        current_time = sum(segment_times[i] for i in current_solution)
        best_solution = current_solution[:]
        best_profit = current_profit

        temperature = initial_temperature

        for iteration in range(max_iterations):
            # Generate a new solution by swapping two segments
            new_solution = current_solution[:]
            i, j = random.sample(range(n), 2)
            new_solution[i], new_solution[j] = new_solution[j], new_solution[i]

            new_profit = sum(segment_profits[k] for k in new_solution)
            new_time = sum(segment_times[k] for k in new_solution)

            if new_time <= time_in_hours * 60:  # Ensure the new solution meets the time constraint
                # Calculate the acceptance probability
                delta_profit = new_profit - current_profit
                acceptance_probability = min(1, math.exp(delta_profit / temperature))

                # Accept the new solution with a certain probability
                if delta_profit > 0 or random.random() < acceptance_probability:
                    current_solution = new_solution
                    current_profit = new_profit
                    current_time = new_time

                    if current_profit > best_profit:
                        best_solution = current_solution
                        best_profit = current_profit

            # Cool down the temperature
            temperature *= cooling_rate

        total_time_hours = sum(segment_times[k] for k in best_solution) / 60

        knapsack_scores.append((formatted_path, best_profit, total_time_hours))

        # Store only the routes that meet the time constraint
        if total_time_hours <= time_in_hours:
            valid_routes.append((formatted_path, best_profit, total_time_hours))

    # Return the calculated scores and valid routes
    return knapsack_scores, valid_routes


# Rest of the code remains the same...

# Calculate knapsack scores for all valid paths and filter based on time


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
    time_in_hours = float(input("Enter the maximum travel time in hours: "))
    avg_speed_kmh = 50

    # Get the search key (current place) from the user
    search_key = input("Enter the current location: ").strip().lower()

    # Fetch the reference point based on the search key
    query = "SELECT id, latitude, longitude FROM dataset WHERE LOWER(TRIM(title)) = %s LIMIT 1"
    cursor.execute(query, (search_key,))
    reference_point = cursor.fetchone()

    if reference_point:
        reference_id, reference_lat, reference_lon = reference_point
        print(f"Reference point found: ID={reference_id}, Lat={reference_lat}, Lon={reference_lon}")
    else:
        print("Search key not found in the dataset.")
        sys.exit()

    # Get the end point (destination place) from the user
    end_key = input("Enter the end location: ").strip().lower()

    # Fetch the end point based on the search key
    query = "SELECT id, latitude, longitude FROM dataset WHERE LOWER(TRIM(title)) = %s LIMIT 1"
    cursor.execute(query, (end_key,))
    end_point = cursor.fetchone()

    if end_point:
        end_id, end_lat, end_lon = end_point
        print(f"End point found: ID={end_id}, Lat={end_lat}, Lon={end_lon}")
    else:
        print("End location not found in the dataset.")
        sys.exit()

    # Fetch the dataset in batches
    query = "SELECT id, place_name, title, latitude, longitude FROM dataset"
    batch_size = 1000
    places = []

    for batch in process_in_batches(cursor, query, batch_size):
        places.extend([(row[0], row[1], row[2], (row[3], row[4])) for row in batch])

        if len(places) > 100000:
            places.clear()

    unique_filtered_places = filter_unique_ids(places)

    # Use the get_filtered_places function to filter the dataset
    start_coords = (reference_lat, reference_lon)
    end_coords = (end_lat, end_lon)

    filtered_places = get_filtered_places(start_coords, end_coords, unique_filtered_places, tolerance=0.01,
                                          max_distance_km=10)

    # Save all intermediate places in a list
    all_places = [(place[0], place[1], place[2], place[3]) for place in filtered_places]

    # Output the results
    #print("\nFiltered Places:")
    #for place in all_places:
        #print(f"ID: {place[0]}, Place Name: {place[1]}, Title: {place[2]}, Coordinates: {place[3]}")

    # Find nearest neighbors and create graph using the filtered list
    max_distance = 50
    connections, coordinates_dict = find_nearest_neighbors(reference_id, end_id, filtered_places, max_distance)

    # Add neighbors for the end point with a different max distance
    end_neighbors = fixed_distance_dijkstra(create_graph(filtered_places), end_id, 130)
    connections.extend((end_id, neighbor) for neighbor in end_neighbors if neighbor != end_id)

    graph = create_graph_from_connections(connections, coordinates_dict)

    # Print graph in the desired format
    #print("\nGraph representation (node: [neighbor, ...]):")
   # for node, neighbors in graph.items():
        #print(f"{node}: {neighbors}")

    # Find and print all possible paths from reference to the end location
    paths = find_all_paths(graph, reference_id, end_id)

    # Create a mapping from place ID to title
    id_to_title = {place[0]: place[2] for place in filtered_places}

    all_paths_titles = []

    #print("\nAll possible paths with titles:")
    for i, path in enumerate(paths, 1):
        if len(path) >= 4:
         path_titles = [id_to_title[place_id] for place_id in path]
         formatted_path = f"{i}: {' -> '.join(path_titles)}"
         all_paths_titles.append((formatted_path, path))

    # Fetch ratings and rating counts for all unique places in the valid paths
    all_place_ids = set(place_id for _, path in all_paths_titles for place_id in path)
    ratings_and_counts = fetch_ratings_and_counts(cursor, all_place_ids)

    # Calculate knapsack scores for all valid paths
    knapsack_scores, valid_routes = calculate_simulated_annealing(all_paths_titles, ratings_and_counts, coordinates_dict,
                                                             time_in_hours, avg_speed_kmh)

    # Print valid routes sorted by Knapsack total score
    #print("\nValid Routes sorted by Knapsack Total Score:")
    #for formatted_path, score, travel_time in knapsack_scores:
        #print(f"Route: {formatted_path}, Score: {score:.2f}, Travel Time: {travel_time:.2f} hours")

    print("\nHere are your curated rote  based recommendations:")
    for formatted_path, score, travel_time in valid_routes:
        print(f"Route: {formatted_path}, Score: {score:.2f}, Travel Time: {travel_time:.2f} hours")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    cursor.close()
    db.close()

end_time = time.time()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")
