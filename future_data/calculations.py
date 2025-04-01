"""
Module for calculating boating conditions based on weather and marine data.
Contains constants, conversions, and assessment logic.
"""

# Constants for condition assessment
GOOD_WAVE_HEIGHT_MAX_FT = 3.0  # in feet (converted from meters)
GOOD_WIND_SPEED_MAX_MPH = 15.0  # in mph (converted from km/h)
MEDIOCRE_WAVE_HEIGHT_MAX_FT = 4.0
MEDIOCRE_WIND_SPEED_MAX_MPH = 18.0
MEDIOCRE_WIND_GUST_MAX_MPH = 25.0
MIN_GOOD_DURATION_HOURS = 3

def convert_wave_height_to_feet(height_m):
    """Convert wave height from meters to feet."""
    return height_m * 3.28084

def convert_wind_speed_to_mph(speed_kmh):
    """Convert wind speed from km/h to mph."""
    return speed_kmh * 0.621371

def assess_hour_condition(wave_height_ft, wind_speed_mph, wind_gust_mph, wave_period, wave_height_m):
    """
    Assess the boating conditions for a single hour.
    
    Args:
        wave_height_ft (float): Wave height in feet
        wind_speed_mph (float): Wind speed in mph
        wind_gust_mph (float): Wind gust speed in mph
        wave_period (float): Wave period in seconds
        wave_height_m (float): Original wave height in meters (for ratio calculation)
        
    Returns:
        str: Rating as "GOOD", "MEDIOCRE", or "BAD"
    """
    # Assess conditions
    is_good = (
        wave_height_ft < GOOD_WAVE_HEIGHT_MAX_FT and
        wind_speed_mph < GOOD_WIND_SPEED_MAX_MPH and
        wave_period >= 2 * wave_height_m
    )
    
    is_bad = (
        wave_height_ft > MEDIOCRE_WAVE_HEIGHT_MAX_FT or
        wind_speed_mph > MEDIOCRE_WIND_SPEED_MAX_MPH or
        wind_gust_mph > MEDIOCRE_WIND_GUST_MAX_MPH
    )
    
    if is_good:
        return "GOOD"
    elif not is_bad:
        return "MEDIOCRE"
    else:
        return "BAD"

def determine_day_rating(hourly_assessments):
    """
    Determine the overall day rating based on hourly assessments.
    
    Args:
        hourly_assessments (list): List of hourly assessment dictionaries
        
    Returns:
        tuple: (day_rating, good_hours_count)
    """
    good_hours = [h for h in hourly_assessments if h["rating"] == "GOOD"]
    good_hours_count = len(good_hours)
    
    if good_hours_count >= MIN_GOOD_DURATION_HOURS:
        day_rating = "GOOD"
    elif all(assessment["rating"] == "BAD" for assessment in hourly_assessments):
        day_rating = "BAD"
    else:
        day_rating = "MEDIOCRE"
        
    return day_rating, good_hours_count 