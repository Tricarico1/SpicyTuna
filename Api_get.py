import requests
import json
from datetime import datetime

# Define the URL
url = "https://www.ndbc.noaa.gov/data/realtime2/41056.txt"

# Make the API call
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Print the raw response text for debugging
    print("Response Text:")
    print(response.text)  # Add this line to see the raw data

    # Convert the text data to a list of lines
    lines = response.text.splitlines()
    
    # Process the lines to create a list of dictionaries
    data = []
    for line in lines:
        # Split the line by spaces
        parts = line.split()
        
        # Ensure the line has the expected number of parts
        if len(parts) >= 14:  # Adjust this number based on the actual number of columns
            entry = {
                "year": parts[0],
                "month": parts[1],
                "day": parts[2],
                "hour": parts[3],
                "minute": parts[4],
                "wind_direction": parts[5],
                "wind_speed": parts[6],
                "gust": parts[7],
                "wave_height": parts[8],
                "dominant_wave_period": parts[9],
                "average_wave_period": parts[10],
                "pressure": parts[11],
                "air_temperature": parts[12],
                "water_temperature": parts[13]
                # Add more fields as needed
            }
            data.append(entry)
    
    # Get the current date and time for the filename
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json_filename = f"json-{current_time}.json"
    txt_filename = f"data-{current_time}.txt"
    
    # Save the data as JSON
    with open(json_filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    # Save the raw text data
    with open(txt_filename, 'w') as txt_file:
        txt_file.write(response.text)
    
    print(f"Data saved to {json_filename} and {txt_filename}")
else:
    print(f"Failed to retrieve data: {response.status_code}")