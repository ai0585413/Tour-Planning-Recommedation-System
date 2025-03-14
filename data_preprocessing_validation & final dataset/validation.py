import json


# Define the validation function
def validate_data(entry):
    errors = []
    missing_fields = []

    # Check for missing required fields
    required_fields = ['id', 'upazila_name', 'title', 'address', 'latitude', 'longitude', 'category', 'rating',
                       'ratingCount']
    for field in required_fields:
        if field not in entry:
            missing_fields.append(field)
            errors.append(f"Missing field: {field}")

    # Validate data types and range if all required fields are present
    if not missing_fields:
        # Validate data types and range here if all required fields are present
        if 'rating' in entry and not (0 <= entry['rating'] <= 5):
            errors.append("Invalid value for 'rating'; expected 0 <= rating <= 5.")
        if 'latitude' in entry and not (-90 <= entry['latitude'] <= 90):
            errors.append("Invalid value for 'latitude'; expected -90 <= latitude <= 90.")
        if 'longitude' in entry and not (-180 <= entry['longitude'] <= 180):
            errors.append("Invalid value for 'longitude'; expected -180 <= longitude <= 180.")

    return errors, missing_fields


# Load the JSON file
with open('tourismdatasetbd.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Validate each entry and capture entries with missing fields
all_errors = {}
missing_entries = {}
for entry in data:
    entry_errors, missing_fields = validate_data(entry)
    if entry_errors:
        all_errors[entry['id']] = entry_errors
    if missing_fields:
        missing_entries[entry['id']] = {"missing_fields": missing_fields, "entry_data": entry}

# Print out entries with missing fields
if missing_entries:
    print("Entries with missing fields:")
    for entry_id, info in missing_entries.items():
        print(f"\nEntry ID {entry_id}: Missing Fields - {info['missing_fields']}")
        print("Entry Data:", info["entry_data"])
else:
    print("No entries with missing fields.")

# Print validation errors if any
if all_errors:
    print("\nData validation errors found:")
    for entry_id, errors in all_errors.items():
        print(f"Entry ID {entry_id}:")
        for error in errors:
            print(f"  - {error}")
else:
    print("All entries passed validation.")
