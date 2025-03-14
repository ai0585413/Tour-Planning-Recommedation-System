import os
import json

# Specify the directory containing JSON files
directory = "E:/class materials/1.Capstone A/json covertion final/TourismDatasetBD"

count = 0
# Iterate over each file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".txt"):  # Check if the file is a JSON file
        file_path = os.path.join(directory, filename)
        # Open the file in read mode
        with open(file_path, "r", encoding='utf-8') as file:
            contents = file.read()
            contents = contents.strip()
            if not contents.startswith("{"):
                contents = "{" + contents

            if not contents.endswith("}"):
                if not contents.endswith("]"):
                    contents = contents + "]"
                contents = contents + "}"
            try:
                #print(contents)
                # Load JSON data from the file
                data = json.loads(contents)
                places = data['places']
                filename = filename.replace(".txt", "")
                key_place = filename.split(" at ")
                search_key = key_place[0]
                place_name = key_place[1]

                for place in places:
                    #print(f"\t {place}")
                    title = place['title']
                    address = ''
                    if 'address' in place:
                        address = place['address']
                    latitude = place['latitude']
                    longitude = place['longitude']
                    category = ''
                    if 'category' in place:
                        category = place['category']
                    rating = -9
                    ratingCount = 0
                    if 'rating' in place:
                        rating = place['rating']
                        ratingCount = place['ratingCount']
                    count = count + 1
                    # Write code to store all data in a database
                    #print(f"{count}.\t{search_key}\t{place_name}\t{rating}\t{ratingCount}\t{latitude}\t{longitude}\t{category}\t{title}\t{address}")
            except:
                print(file_path)