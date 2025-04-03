"""
Module for fetching weather and marine data from APIs.
"""
import copy
import pandas as pd
import meteo_marine
import meteo_weather

def fetch_weather_data(latitude, longitude):
    """
    Fetch weather data for the given location.
    
    Args:
        latitude (float): Location latitude
        longitude (float): Location longitude
        
    Returns:
        pd.DataFrame: Weather data with hourly forecasts
    """
    # Make a copy of the meteo_weather module's params and update coordinates
    params = copy.deepcopy(meteo_weather.params)
    params["latitude"] = latitude
    params["longitude"] = longitude
    
    # Use the Open-Meteo client to get weather data
    responses = meteo_weather.openmeteo.weather_api(meteo_weather.url, params=params)
    response = responses[0]
    
    # Process the data
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
    """
    Fetch marine data for the given location.
    
    Args:
        latitude (float): Location latitude
        longitude (float): Location longitude
        
    Returns:
        pd.DataFrame: Marine data with hourly forecasts
    """
    # Make a copy of the meteo_marine module's params and update coordinates
    params = copy.deepcopy(meteo_marine.params)
    params["latitude"] = latitude
    params["longitude"] = longitude
    
    # Use the Open-Meteo client to get marine data
    responses = meteo_marine.openmeteo.weather_api(meteo_marine.url, params=params)
    response = responses[0]
    
    # Process the data
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