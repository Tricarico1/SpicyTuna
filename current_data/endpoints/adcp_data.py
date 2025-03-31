from datetime import datetime
import math

def get_adcp_data(station_id):
    """Get ADCP current data from NDBC"""
    url = f"https://www.ndbc.noaa.gov/data/realtime2/{station_id}.adcp"
    return {
        "name": "adcp",
        "url": url,
        "description": "Acoustic Doppler Current Profiler data"
    }

def process_adcp_data(lines):
    """Process ADCP data lines and return relevant data points"""
    data_points = []
    
    for line in lines:
        if not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 60:  # Ensure we have enough fields
                # Create base data point with timestamp
                data_point = {
                    'timestamp': f"{parts[0]}-{parts[1]}-{parts[2]} {parts[3]}:{parts[4]}"
                }
                
                # Process depth, direction, and speed measurements
                for i in range(20):  # Process 20 depth levels
                    base_idx = 5 + i * 3  # Each measurement has 3 values
                    depth = float(parts[base_idx])
                    direction = int(parts[base_idx + 1])
                    speed = float(parts[base_idx + 2])
                    
                    data_point[f'depth_{i+1}'] = depth
                    data_point[f'direction_{i+1}'] = direction
                    data_point[f'speed_{i+1}'] = speed
                
                data_points.append(data_point)
    
    return data_points

def calculate_adcp_statistics(data_points):
    """Calculate statistics for ADCP current data"""
    if not data_points:
        print("No ADCP data points available")
        return
    
    # Calculate average speed and direction for each depth level
    for level in range(1, 21):  # For all 20 depth levels
        speeds = []
        directions = []
        depth = None
        
        for point in data_points:
            speed = point[f'speed_{level}']
            direction = point[f'direction_{level}']
            if depth is None:
                depth = point[f'depth_{level}']
            
            if speed != 0:  # Only include non-zero speeds
                speeds.append(speed)
            if direction != 0:  # Only include non-zero directions
                directions.append(direction)
        
        if speeds and directions:
            avg_speed = sum(speeds) / len(speeds)
            # For direction, we need to handle the circular nature of degrees
            sin_sum = sum(math.sin(math.radians(d)) for d in directions)
            cos_sum = sum(math.cos(math.radians(d)) for d in directions)
            avg_direction = math.degrees(math.atan2(sin_sum, cos_sum)) % 360
            
            print(f"\nDepth {depth:.1f}m:")
            print(f"  Average Speed: {avg_speed:.1f} cm/s")
            print(f"  Average Direction: {avg_direction:.1f}°") 