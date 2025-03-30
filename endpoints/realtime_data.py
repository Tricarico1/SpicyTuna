from datetime import datetime
import requests

def get_realtime_data(station_id):
    """Get realtime data from NDBC"""
    url = f"https://www.ndbc.noaa.gov/data/realtime2/{station_id}.txt"
    return {
        "name": "realtime",
        "url": url,
        "description": "Realtime meteorological data"
    }

def process_realtime_data(lines):
    """Process realtime data lines and return relevant data points"""
    data_points = []
    
    for line in lines:
        if not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 19:
                data_point = {
                    'timestamp': f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}:{parts[4]}",
                    'wind_speed': float(parts[6]) if parts[6] != 'MM' else None,
                    'wave_height': float(parts[8]) if parts[8] != 'MM' else None,
                }
                data_points.append(data_point)
    
    return data_points

def calculate_realtime_statistics(data_points):
    """Calculate statistics for realtime data"""
    valid_wind_speeds = [point['wind_speed'] for point in data_points if point['wind_speed'] is not None]
    valid_wave_heights = [point['wave_height'] for point in data_points if point['wave_height'] is not None]
    
    if valid_wind_speeds:
        avg_wind_speed = sum(valid_wind_speeds) / len(valid_wind_speeds)
        print(f"Average wind speed: {avg_wind_speed:.2f}")
    
    if valid_wave_heights:
        avg_wave_height = sum(valid_wave_heights) / len(valid_wave_heights)
        print(f"Average wave height: {avg_wave_height:.2f}") 