from datetime import datetime
import requests
from endpoints import spectral_data, realtime_data, derived_data, adcp_data
from delete import cleanup_data_files

# Define the station IDs to monitor
STATION_IDS = ["41056"]  

def download_and_save_data(url, endpoint_name, station_id):
    """Download data from URL and save to file"""
    response = requests.get(url)
    if response.status_code == 200:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data_{station_id}_{endpoint_name}_{current_time}.txt"
        
        with open(filename, 'w') as file:
            file.write(response.text)
        
        print(f"Data saved to {filename}")
        return response.text.splitlines()
    else:
        print(f"Failed to retrieve data from {endpoint_name} for station {station_id}: {response.status_code}")
        return None

def main():
    # Get endpoint configurations
    endpoint_types = [
        realtime_data.get_realtime_data,
        spectral_data.get_spectral_data,
        derived_data.get_derived_data,
        adcp_data.get_adcp_data
    ]
    
    # Process each station
    for station_id in STATION_IDS:
        print(f"\nProcessing station {station_id}:")
        
        # Process each endpoint type for this station
        for get_endpoint in endpoint_types:
            endpoint = get_endpoint(station_id)
            print(f"\nProcessing {endpoint['name']} endpoint:")
            lines = download_and_save_data(endpoint['url'], endpoint['name'], station_id)
            
            if lines:
                if endpoint['name'] == 'realtime':
                    data_points = realtime_data.process_realtime_data(lines)
                    realtime_data.calculate_realtime_statistics(data_points)
                elif endpoint['name'] == 'spectral':
                    data_points = spectral_data.process_spectral_data(lines)
                    spectral_data.calculate_spectral_statistics(data_points)
                elif endpoint['name'] == 'derived':
                    data_points = derived_data.process_derived_data(lines)
                    derived_data.calculate_derived_statistics(data_points)
                elif endpoint['name'] == 'adcp':
                    data_points = adcp_data.process_adcp_data(lines)
                    adcp_data.calculate_adcp_statistics(data_points)

if __name__ == "__main__":
    # Uncomment the next line to delete old data files before running
    cleanup_data_files()
    main()