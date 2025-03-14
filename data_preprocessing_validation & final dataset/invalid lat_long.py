import json

# Define the validation function
def validate_data(entry):
    errors = []
    invalid_lat_lng = False  # Flag for invalid latitude/longitude

    # Check for missing required fields
    required_fields = ['id', 'latitude', 'longitude']
    for field in required_fields:
        if field not in entry:
            errors.append(f"Missing field: {field}")
            return errors, invalid_lat_lng  # Skip further validation if required fields are missing

    # Validate latitude and longitude
    if not (-90 <= entry['latitude'] <= 90):
        errors.append(f"Invalid latitude: {entry['latitude']} (expected -90 <= latitude <= 90).")
        invalid_lat_lng = True
    if not (-180 <= entry['longitude'] <= 180):
        errors.append(f"Invalid longitude: {entry['longitude']} (expected -180 <= longitude <= 180).")
        invalid_lat_lng = True

    return errors, invalid_lat_lng


# Load the JSON file
with open('E:/class materials/1.Capstone A/json covertion final/Prepossessing_Copy/tourismdatasetbd.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Validate each entry and capture invalid latitude/longitude entries
invalid_lat_lng_ids = []
for entry in data:
    entry_errors, invalid_lat_lng = validate_data(entry)
    if invalid_lat_lng:
        invalid_lat_lng_ids.append(entry['id'])

# Print IDs with invalid latitude or longitude
if invalid_lat_lng_ids:
    print("Entries with invalid latitude or longitude:")
    print(invalid_lat_lng_ids)
else:
    print("No entries with invalid latitude or longitude.")
