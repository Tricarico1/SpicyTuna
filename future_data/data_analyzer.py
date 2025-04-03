"""
Module for analyzing weather and marine data and assessing boating conditions.
"""
import pandas as pd
from datetime import datetime
import astral
from astral.sun import sun
from astral import LocationInfo
import calculations

def get_location_info(loc_data):
    """
    Create an astral LocationInfo object from location data.
    
    Args:
        loc_data (dict): Location data dictionary
        
    Returns:
        LocationInfo: Astral location info object
    """
    return LocationInfo(
        name=loc_data["name"],
        region=loc_data["region"],
        timezone=loc_data["timezone"],
        latitude=loc_data["latitude"],
        longitude=loc_data["longitude"]
    )

def get_sunrise_sunset(date, location_info):
    """
    Get sunrise and sunset times for the given date and location.
    
    Args:
        date (date): Date to get sunrise/sunset for
        location_info (LocationInfo): Astral location info
        
    Returns:
        tuple: (sunrise, sunset) datetime objects
    """
    s = sun(location_info.observer, date=date)
    return s['sunrise'], s['sunset']

def analyze_conditions(marine_df, weather_df, location_info):
    """
    Analyze boating conditions from marine and weather data.
    
    Args:
        marine_df (DataFrame): Marine forecast data
        weather_df (DataFrame): Weather forecast data
        location_info (LocationInfo): Location information
        
    Returns:
        dict: Results dictionary with daily and hourly assessments
    """
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
        
        # Assess each hour
        hourly_assessments = []
        
        for _, hour_data in day_data.iterrows():
            hour_str = hour_data['date'].strftime("%H:%M")
            
            # Convert measurements to required units
            wave_height_ft = calculations.convert_wave_height_to_feet(hour_data['wave_height'])
            wind_speed_mph = calculations.convert_wind_speed_to_mph(hour_data['wind_speed_10m'])
            wind_gust_mph = calculations.convert_wind_speed_to_mph(hour_data['wind_gusts_10m'])
            wave_period = hour_data['wave_period']
            
            # Use calculations module to assess conditions
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
        
        # Determine overall day rating using calculations module
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

def find_good_days(all_results):
    """
    Filter results to only include good boating days.
    
    Args:
        all_results (dict): All boating conditions results
        
    Returns:
        dict: Filtered results with only good days
    """
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