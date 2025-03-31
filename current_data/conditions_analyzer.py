from datetime import datetime

class ConditionsAnalyzer:
    def __init__(self):
        self.ratings = {
            'BAD': 0,
            'MEDIOCRE': 1,
            'GREAT': 2
        }

    def analyze_conditions(self, data_points):
        """Analyze conditions from all data sources and return a rating"""
        if not data_points or not all(key in data_points for key in ['wave', 'wind', 'spectral']):
            print("Missing required data for analysis")
            return None

        wave_data = data_points['wave']
        wind_data = data_points['wind']
        spectral_data = data_points['spectral']

        # Check for BAD conditions first (any single bad condition makes it a bad day)
        if self._is_bad_conditions(wave_data, wind_data):
            return 'BAD'

        # Check for GREAT conditions (all conditions must be met)
        if self._is_great_conditions(wave_data, wind_data, spectral_data):
            return 'GREAT'

        # If neither BAD nor GREAT, it's MEDIOCRE
        return 'MEDIOCRE'

    def _is_bad_conditions(self, wave_data, wind_data):
        """Check if any conditions are in the BAD category"""
        # Get values with defaults
        wave_height = wave_data.get('wave_height', 0) or 0
        wave_period = wave_data.get('wave_period', 0) or 0
        wind_speed = wind_data.get('wind_speed', 0) or 0
        wind_gust = wind_data.get('wind_gust', 0) or 0

        # Wave height > 4 feet
        if wave_height * 3.28084 > 4:  # Convert meters to feet
            return True

        # Wave period and height interaction
        if (wave_period < 5 and wave_height * 3.28084 > 3) or (wave_period > 10 and wave_height * 3.28084 > 4):
            return True

        # Wind speed > 18 mph
        if wind_speed * 2.237 > 18:  # Convert m/s to mph
            return True

        # Wind gusts > 25 mph
        if wind_gust * 2.237 > 25:  # Convert m/s to mph
            return True

        return False

    def _is_great_conditions(self, wave_data, wind_data, spectral_data):
        """Check if all conditions meet GREAT criteria"""
        # Get values with defaults
        wave_height = wave_data.get('wave_height', 0) or 0
        wave_period = wave_data.get('wave_period', 0) or 0
        wind_speed = wind_data.get('wind_speed', 0) or 0
        wind_gust = wind_data.get('wind_gust', 0) or 0

        # Wave height < 2 feet
        if wave_height * 3.28084 >= 2:  # Convert meters to feet
            return False

        # Wave period > 7 seconds
        if wave_period <= 7:
            return False

        # Wind speed < 10 mph
        if wind_speed * 2.237 >= 10:  # Convert m/s to mph
            return False

        # Wind gusts < 15 mph
        if wind_gust * 2.237 >= 15:  # Convert m/s to mph
            return False

        # Check wave period is at least 2x the wave height
        if wave_period < wave_height * 2:
            return False

        return True

    def get_detailed_analysis(self, data_points):
        """Return detailed analysis of conditions"""
        rating = self.analyze_conditions(data_points)
       
        # Get values with defaults and handle None values
        wave_height = data_points['wave'].get('wave_height', 0) or 0
        wave_period = data_points['wave'].get('wave_period', 0) or 0
        wind_speed = data_points['wind'].get('wind_speed', 0) or 0
        wind_gust = data_points['wind'].get('wind_gust', 0) or 0
       
        details = {
            'rating': rating,
            'wave_height_ft': wave_height * 3.28084,
            'wave_period_sec': wave_period,
            'wind_speed_mph': wind_speed * 2.237,
            'wind_gust_mph': wind_gust * 2.237,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return details 