import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://marine-api.open-meteo.com/v1/marine"
params = {
	"latitude": 18.376,
	"longitude": 67.280,
	"hourly": ["wave_height", "wind_wave_height", "wind_wave_direction", "wave_direction", "wave_period", "swell_wave_height", "swell_wave_direction", "swell_wave_period", "swell_wave_peak_period", "wind_wave_period", "wind_wave_peak_period"],
	"timezone": "America/New_York",
	"forecast_days": 16
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

							# Process hourly data. The order of variables needs to be the same as requested.
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

hourly_dataframe = pd.DataFrame(data = hourly_data)
# print(hourly_dataframe)

