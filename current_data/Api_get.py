from datetime import datetime
import requests
from endpoints import spectral_data, realtime_data, derived_data, adcp_data
from delete import cleanup_data_files
from conditions_analyzer import ConditionsAnalyzer

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

def combine_data_points(realtime_points, spectral_points, derived_points):
    """Combine data from different sources for analysis"""
    if not all([realtime_points, spectral_points, derived_points]):
        return None
    
    # Ensure we have data points before accessing
    if not (realtime_points and spectral_points and derived_points):
        return None
    
    # Get the most recent data point from each source
    combined = {
        'wave': {
            'wave_height': realtime_points[0].get('wave_height', 0),
            'wave_period': spectral_points[0].get('mean_wave_period', 0)
        },
        'wind': {
            'wind_speed': realtime_points[0].get('wind_speed', 0),
            'wind_gust': derived_points[0].get('wind_speed_10m', 0)  # Using 10m wind as gust
        },
        'spectral': {
            'steepness': spectral_points[0].get('steepness', 'N/A')
        }
    }
    return combined

def main():
    analyzer = ConditionsAnalyzer()
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
        
        realtime_points = None
        spectral_points = None
        derived_points = None
        
        # Process each endpoint type for this station
        for get_endpoint in endpoint_types:
            endpoint = get_endpoint(station_id)
            print(f"\nProcessing {endpoint['name']} endpoint:")
            lines = download_and_save_data(endpoint['url'], endpoint['name'], station_id)
            
            if lines:
                if endpoint['name'] == 'realtime':
                    realtime_points = realtime_data.process_realtime_data(lines)
                    realtime_data.calculate_realtime_statistics(realtime_points)
                elif endpoint['name'] == 'spectral':
                    spectral_points = spectral_data.process_spectral_data(lines)
                    spectral_data.calculate_spectral_statistics(spectral_points)
                elif endpoint['name'] == 'derived':
                    derived_points = derived_data.process_derived_data(lines)
                    derived_data.calculate_derived_statistics(derived_points)
                elif endpoint['name'] == 'adcp':
                    data_points = adcp_data.process_adcp_data(lines)
                    adcp_data.calculate_adcp_statistics(data_points)
        
        # Analyze combined conditions
        combined_data = combine_data_points(realtime_points, spectral_points, derived_points)
        if combined_data:
            analysis = analyzer.get_detailed_analysis(combined_data)
            print("\nConditions Analysis:")
            print(f"Rating: {analysis['rating']}")
            print(f"Wave Height: {analysis['wave_height_ft']:.1f} ft")
            print(f"Wave Period: {analysis['wave_period_sec']:.1f} sec")
            print(f"Wind Speed: {analysis['wind_speed_mph']:.1f} mph")
            print(f"Wind Gusts: {analysis['wind_gust_mph']:.1f} mph")

if __name__ == "__main__":
    # Uncomment the next line to delete old data files before running
    cleanup_data_files()
    main()