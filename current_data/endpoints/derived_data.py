from datetime import datetime
import requests

def get_derived_data(station_id):
    """Get derived meteorological data from NDBC"""
    url = f"https://www.ndbc.noaa.gov/data/derived2/{station_id}.dmv"
    return {
        "name": "derived",
        "url": url,
        "description": "Derived meteorological values"
    }

def process_derived_data(lines):
    """Process derived data lines and return relevant data points"""
    data_points = []
    
    for line in lines:
        if not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 9:  # Ensure we have all needed fields
                data_point = {
                    'timestamp': f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}:{parts[4]}",
                    'wind_chill': float(parts[5]) if parts[5] != 'MM' else None,
                    'heat_index': float(parts[6]) if parts[6] != 'MM' else None,
                    'ice_accretion': float(parts[7]) if parts[7] != 'MM' else None,
                    'wind_speed_10m': float(parts[8]) if parts[8] != 'MM' else None,
                    'wind_speed_20m': float(parts[9]) if parts[9] != 'MM' else None
                }
                data_points.append(data_point)
    
    return data_points

def calculate_derived_statistics(data_points):
    """Calculate statistics for derived meteorological data"""
    # Calculate wind speed statistics at 10m and 20m
    valid_wind_10m = [point['wind_speed_10m'] for point in data_points if point['wind_speed_10m'] is not None]
    valid_wind_20m = [point['wind_speed_20m'] for point in data_points if point['wind_speed_20m'] is not None]
    
    if valid_wind_10m:
        avg_wind_10m = sum(valid_wind_10m) / len(valid_wind_10m)
        max_wind_10m = max(valid_wind_10m)
        print(f"Wind speed at 10m:")
        print(f"  Average: {avg_wind_10m:.2f} m/s")
        print(f"  Maximum: {max_wind_10m:.2f} m/s")
    
    if valid_wind_20m:
        avg_wind_20m = sum(valid_wind_20m) / len(valid_wind_20m)
        max_wind_20m = max(valid_wind_20m)
        print(f"\nWind speed at 20m:")
        print(f"  Average: {avg_wind_20m:.2f} m/s")
        print(f"  Maximum: {max_wind_20m:.2f} m/s")
    
    # Calculate heat index statistics if available
    valid_heat = [point['heat_index'] for point in data_points if point['heat_index'] is not None]
    if valid_heat:
        avg_heat = sum(valid_heat) / len(valid_heat)
        max_heat = max(valid_heat)
        print(f"\nHeat index:")
        print(f"  Average: {avg_heat:.2f}°C")
        print(f"  Maximum: {max_heat:.2f}°C") 