import json

# Define the validation function
def check_missing_lat_lng(entry):
    missing_fields = []
    if 'latitude' not in entry:
        missing_fields.append('latitude')
    if 'longitude' not in entry:
        missing_fields.append('longitude')
    return missing_fields


# Load the JSON file
with open('E:/class materials/1.Capstone A/json covertion final/Prepossessing_Copy/tourismdatasetbd.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Track entries with missing latitude or longitude
missing_lat_lng_entries = {}
for entry in data:
    missing_fields = check_missing_lat_lng(entry)
    if missing_fields:
        missing_lat_lng_entries[entry['id']] = {
            "missing_fields": missing_fields,
            "entry_data": entry
        }

# Print entries with missing latitude or longitude
if missing_lat_lng_entries:
    print("Entries with missing latitude or longitude:")
    for entry_id, info in missing_lat_lng_entries.items():
        print(f"\nEntry ID {entry_id}: Missing Fields - {info['missing_fields']}")
        print("Entry Data:", info["entry_data"])
else:
    print("No entries with missing latitude or longitude.")
