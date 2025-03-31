from datetime import datetime
import requests

def get_spectral_data(station_id):
    """Get spectral wave data from NDBC"""
    url = f"https://www.ndbc.noaa.gov/data/realtime2/{station_id}.spec"
    return {
        "name": "spectral",
        "url": url,
        "description": "Spectral wave data"
    }

def process_spectral_data(lines):
    """Process spectral data lines and return relevant data points"""
    data_points = []
    
    for line in lines:
        if not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 15:  # Ensure we have all needed fields
                data_point = {
                    'timestamp': f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}:{parts[4]}",
                    'wave_height': float(parts[5]) if parts[5] != 'MM' else None,
                    'steepness': parts[12] if parts[12] != 'MM' else None,
                    'mean_wave_direction': float(parts[14]) if parts[14] != 'MM' else None
                }
                data_points.append(data_point)
    
    return data_points

def calculate_spectral_statistics(data_points):
    """Calculate statistics for spectral data"""
    valid_heights = [point['wave_height'] for point in data_points if point['wave_height'] is not None]
    
    if valid_heights:
        avg_height = sum(valid_heights) / len(valid_heights)
        max_height = max(valid_heights)
        print(f"Average wave height: {avg_height:.2f}m")
        print(f"Maximum wave height: {max_height:.2f}m")
        
    # Count steepness categories
    steepness_counts = {}
    for point in data_points:
        if point['steepness']:
            steepness_counts[point['steepness']] = steepness_counts.get(point['steepness'], 0) + 1
    
    if steepness_counts:
        print("\nWave steepness distribution:")
        for category, count in steepness_counts.items():
            print(f"{category}: {count}") 