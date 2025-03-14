import json

def filter_and_reorder_places(json_file, output_file):
    # Define the key order to keep
    key_order = ['id', 'upazila_name', 'search_key', 'title', 'address', 'latitude', 'longitude', 'category', 'rating', 'ratingCount']

    # Define limits for latitude and longitude
    lat_lower_limit = 20.2436
    lat_upper_limit = 27.5653
    lon_lower_limit = 86.9172
    lon_upper_limit = 93.4179

    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Start unique ID counter
    unique_id = 1
    filtered_data = []

    # Iterate over each place in the data list
    for place in data:
        # Filter out places where the address contains "West Bengal"
        if "West Bengal" in place.get("address", ""):
            continue
            # Filter out places where the address contains "West Bengal"
        if "India" in place.get("address", ""):
                continue

        # Filter out places with latitude or longitude outside the defined limits
        latitude = place.get('latitude')
        longitude = place.get('longitude')
        if latitude is None or longitude is None:
            continue  # Skip if latitude or longitude is not present

        if not (lat_lower_limit <= latitude <= lat_upper_limit and lon_lower_limit <= longitude <= lon_upper_limit):
            continue  # Skip if latitude or longitude is out of bounds

        # Fill missing rating and ratingCount values
        if 'rating' not in place:
            place['rating'] = -9
        if 'ratingCount' not in place:
            place['ratingCount'] = 0

        # Assign a unique ID
        place['id'] = unique_id
        unique_id += 1

        # Reorder keys and keep only those in key_order
        reordered_place = {key: place[key] for key in key_order if key in place}

        # Append the filtered and reordered place if it's not empty
        if reordered_place:
            filtered_data.append(reordered_place)

    # Save the modified data to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=4, ensure_ascii=False)

    print(f"Filtered, reordered, outlier-removed, missing values filled, and IDs reset JSON data saved to {output_file}")

# Specify the path to the original and output JSON files
json_file = 'E:/class materials/1.Capstone A/json covertion final/merged_output.json'  # Path to your input JSON file
output_file = 'E:/class materials/1.Capstone A/json covertion final/tourismdatasetbd.json'  # Path to save the modified JSON file

# Run the function
filter_and_reorder_places(json_file, output_file)
