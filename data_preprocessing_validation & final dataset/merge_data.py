import os
import json

# Directory containing the text files
input_folder = 'E:/class materials/1.Capstone A/json covertion final/TourismDatasetBD'
output_file = 'merged_output.json'

merged_data = []

# Iterate over each file in the directory
for filename in os.listdir(input_folder):
    if filename.endswith('.txt'):
        # Split the filename to extract upazila_name and search_key
        parts = filename.replace('.txt', '').split(' at ')
        if len(parts) == 2:
            search_key = parts[0].strip()
            upazila_name = parts[1].strip()

            # Read the content of the file
            with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as file:
                file_content = json.load(file)

            # Add extracted data to each object in the file content
            for entry in file_content.get("places", []):
                entry['upazila_name'] = upazila_name
                entry['search_key'] = search_key
                merged_data.append(entry)

# Write the merged data to a JSON file
with open(output_file, 'w', encoding='utf-8') as output_json:
    json.dump(merged_data, output_json, ensure_ascii=False, indent=4)

print(f'Merged JSON data written to {output_file}')
