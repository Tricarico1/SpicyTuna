import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import astral
from astral.sun import sun
from astral import LocationInfo
import table_generation  # Import the table generation module
import calculations  # Import the new calculations module

# Import the modules (assuming they're in the same directory)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import meteo_marine
import meteo_weather
import locations  # Import the locations module
import delete  # Import the cleanup module

# Constants moved to calculations.py

def get_location_info(loc_data):
    """Create an astral LocationInfo object from location data."""
    return LocationInfo(
        name=loc_data["name"],
        region=loc_data["region"],
        timezone=loc_data["timezone"],
        latitude=loc_data["latitude"],
        longitude=loc_data["longitude"]
    )

def get_sunrise_sunset(date, location_info):
    """Get sunrise and sunset times for the given date and location."""
    s = sun(location_info.observer, date=date)
    return s['sunrise'], s['sunset']

# Unit conversion functions moved to calculations.py

def fetch_weather_data(latitude, longitude):
    """Fetch weather data for the given location."""
    # Make a copy of the meteo_weather module's params and update coordinates
    import copy
    params = copy.deepcopy(meteo_weather.params)
    params["latitude"] = latitude
    params["longitude"] = longitude
    
    # Use the Open-Meteo client to get weather data
    responses = meteo_weather.openmeteo.weather_api(meteo_weather.url, params=params)
    response = responses[0]
    
    # Process the data similar to meteo_weather.py
    hourly = response.Hourly()
    hourly_wind_speed_10m = hourly.Variables(0).ValuesAsNumpy()
    hourly_wind_gusts_10m = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(3).ValuesAsNumpy()
    hourly_visibility = hourly.Variables(4).ValuesAsNumpy()
    hourly_rain = hourly.Variables(5).ValuesAsNumpy()
    
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
    hourly_data["visibility"] = hourly_visibility
    hourly_data["rain"] = hourly_rain
    
    return pd.DataFrame(data = hourly_data)

def fetch_marine_data(latitude, longitude):
    """Fetch marine data for the given location."""
    # Make a copy of the meteo_marine module's params and update coordinates
    import copy
    params = copy.deepcopy(meteo_marine.params)
    params["latitude"] = latitude
    params["longitude"] = longitude
    
    # Use the Open-Meteo client to get marine data
    responses = meteo_marine.openmeteo.weather_api(meteo_marine.url, params=params)
    response = responses[0]
    
    # Process the data similar to meteo_marine.py
    hourly = response.Hourly()
    hourly_wave_height = hourly.Variables(0).ValuesAsNumpy()
    hourly_wind_wave_height = hourly.Variables(1).ValuesAsNumpy()
    hourly_wind_wave_direction = hourly.Variables(2).ValuesAsNumpy()
    hourly_wave_direction = hourly.Variables(3).ValuesAsNumpy()
    hourly_wave_period = hourly.Variables(4).ValuesAsNumpy()
    hourly_swell_wave_height = hourly.Variables(5).ValuesAsNumpy()
    hourly_swell_wave_direction = hourly.Variables(6).ValuesAsNumpy()
    hourly_swell_wave_period = hourly.Variables(7).ValuesAsNumpy()
    hourly_swell_wave_peak_period = hourly.Variables(8).ValuesAsNumpy()
    hourly_wind_wave_period = hourly.Variables(9).ValuesAsNumpy()
    hourly_wind_wave_peak_period = hourly.Variables(10).ValuesAsNumpy()
    
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    
    hourly_data["wave_height"] = hourly_wave_height
    hourly_data["wind_wave_height"] = hourly_wind_wave_height
    hourly_data["wind_wave_direction"] = hourly_wind_wave_direction
    hourly_data["wave_direction"] = hourly_wave_direction
    hourly_data["wave_period"] = hourly_wave_period
    hourly_data["swell_wave_height"] = hourly_swell_wave_height
    hourly_data["swell_wave_direction"] = hourly_swell_wave_direction
    hourly_data["swell_wave_period"] = hourly_swell_wave_period
    hourly_data["swell_wave_peak_period"] = hourly_swell_wave_peak_period
    hourly_data["wind_wave_period"] = hourly_wind_wave_period
    hourly_data["wind_wave_peak_period"] = hourly_wind_wave_peak_period
    
    return pd.DataFrame(data = hourly_data)

def assess_hourly_conditions(marine_df, weather_df, location_info):
    """Assess the boating conditions for each hour and return as a dictionary."""
    # Merge dataframes on datetime
    merged_df = pd.merge(
        marine_df, 
        weather_df,
        on='date',
        how='inner'
    )
    
    # Create results container
    results = {}
    
    # Group by date (YYYY-MM-DD) to assess daily conditions
    for day, day_data in merged_df.groupby(merged_df['date'].dt.date):
        date_str = day.strftime("%Y-%m-%d")
        sunrise, sunset = get_sunrise_sunset(day, location_info)
        
        # Use all hours instead of filtering for daylight
        # Assess each hour
        hourly_assessments = []
        
        for _, hour_data in day_data.iterrows():
            hour_str = hour_data['date'].strftime("%H:%M")
            
            # Convert measurements to required units
            wave_height_ft = calculations.convert_wave_height_to_feet(hour_data['wave_height'])
            wind_speed_mph = calculations.convert_wind_speed_to_mph(hour_data['wind_speed_10m'])
            wind_gust_mph = calculations.convert_wind_speed_to_mph(hour_data['wind_gusts_10m'])
            wave_period = hour_data['wave_period']
            
            # Use the new function to assess conditions
            rating = calculations.assess_hour_condition(
                wave_height_ft, 
                wind_speed_mph, 
                wind_gust_mph, 
                wave_period, 
                hour_data['wave_height']
            )
                
            # Store hourly assessment
            hourly_assessments.append({
                "time": hour_str,
                "rating": rating,
                "wave_height_ft": round(wave_height_ft, 1),
                "wind_speed_mph": round(wind_speed_mph, 1),
                "wind_gust_mph": round(wind_gust_mph, 1),
                "wave_period_sec": round(wave_period, 1),
                "precipitation_probability": hour_data.get('precipitation_probability', 0),
                "visibility": hour_data.get('visibility', None),
                "rain": hour_data.get('rain', 0)
            })
        
        # Determine overall day rating using the new function
        day_rating, good_hours_count = calculations.determine_day_rating(hourly_assessments)
            
        # Store daily results with hourly assessments
        results[date_str] = {
            "day_rating": day_rating,
            "sunrise": sunrise.strftime("%H:%M"),
            "sunset": sunset.strftime("%H:%M"),
            "good_hours_count": good_hours_count,
            "hourly": hourly_assessments
        }
    
    return results

def process_location(loc_data, location_index):
    """Process a single location and return its boating conditions."""
    print(f"Processing location: {loc_data['name']}, {loc_data['region']}")
    
    # Create location info for sunrise/sunset calculations
    location_info = get_location_info(loc_data)
    
    # Fetch data for the location
    weather_df = fetch_weather_data(loc_data["latitude"], loc_data["longitude"])
    marine_df = fetch_marine_data(loc_data["latitude"], loc_data["longitude"])
    
    # Assess conditions
    results = assess_hourly_conditions(marine_df, weather_df, location_info)
    
    # Return results
    return loc_data['name'], results

def analyze_all_locations():
    """Process all locations and return their boating conditions."""
    all_results = {}
    
    # Process all locations
    for i, location in enumerate(locations.LOCATIONS):
        location_name, results = process_location(location, i)
        all_results[location_name] = results
    
    return all_results

def find_good_days(all_results):
    """Filter the results to only include good days."""
    good_days_results = {}
    
    for location_name, results in all_results.items():
        # Filter for good days only
        good_days = {}
        for date, data in results.items():
            if data['day_rating'] in ['GOOD', 'GREAT']:
                # Clone the data but only include hourly entries with GOOD ratings
                good_day_data = data.copy()
                good_hours = [hour for hour in data['hourly'] if hour['rating'] == 'GOOD']
                good_day_data['hourly'] = good_hours
                good_days[date] = good_day_data
        
        if good_days:
            good_days_results[location_name] = good_days
    
    return good_days_results

def run_analysis():
    """Run the full analysis and return all results and good days"""
    # Get the forecast data for all locations
    all_results = analyze_all_locations()
    
    # Filter for the good days
    good_days_results = find_good_days(all_results)
    
    # Comment out or remove this line since print_summary isn't defined
    # print_summary(all_results, good_days_results)
    
    return all_results, good_days_results

def main():
    # Clean up old JSON files
    delete.cleanup_json_files()
    
    # Process all locations using the refactored function
    all_results = analyze_all_locations()
    good_days_results = find_good_days(all_results)
    
    # Output combined results
    with open("all_boating_conditions.json", 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Output only good days
    with open("good_boating_days.json", 'w') as f:
        json.dump(good_days_results, f, indent=2)
    
    # Generate HTML tables for ALL days (not just good days)
    html_content = table_generation.generate_html_tables(all_results)
    with open("all_boating_conditions.html", "w") as f:
        f.write(html_content)
    print("\nHTML report generated: all_boating_conditions.html")
    
    # Try to open the HTML file in the default browser
    try:
        import webbrowser
        import os
        file_path = os.path.abspath("all_boating_conditions.html")
        webbrowser.open('file://' + file_path)
        print(f"Opened HTML report in browser")
    except Exception as e:
        print(f"Could not open HTML file automatically. Please open it manually: {e}")
    
    # Print summary to console
    print("\nBoating Conditions Summary:")
    for location_name, location_results in all_results.items():
        print(f"\n=== {location_name} ===")
        for date, data in location_results.items():
            print(f"\n{date}: {data['day_rating']}")
            print(f"  Sunrise: {data['sunrise']}, Sunset: {data['sunset']}")
            print(f"  Good hours: {data['good_hours_count']}")
            
            # Print the first 3 hours as example
            print("  Sample hourly ratings:")
            for i, hour in enumerate(data['hourly'][:3]):
                print(f"    {hour['time']}: {hour['rating']} - Wave: {hour['wave_height_ft']}ft, Wind: {hour['wind_speed_mph']}mph")
            if len(data['hourly']) > 3:
                print(f"    ... and {len(data['hourly']) - 3} more hours")
    
    # Print good days summary with time ranges
    if good_days_results:
        print("\n\n=== GOOD BOATING DAYS ===")
        for location_name, good_days in good_days_results.items():
            print(f"\n{location_name}:")
            for date, data in good_days.items():
                # Find the time range
                good_hours = data['hourly']
                if good_hours:
                    first_good_hour = good_hours[0]['time']
                    last_good_hour = good_hours[-1]['time']
                    time_range = f"{first_good_hour} - {last_good_hour}"
                    print(f"  {date}: {data['day_rating']} - {len(good_hours)} good hours ({time_range})")
                else:
                    print(f"  {date}: {data['day_rating']} - 0 good hours")

def get_current_date():
    """Return the current date as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":
    main() 