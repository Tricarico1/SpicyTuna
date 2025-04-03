"""
Main module for boating conditions forecasting.
Coordinates all the other modules to generate the forecast.
"""
import sys
import os
import json
import webbrowser
from datetime import datetime

# Add the module directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
import table_generation
import data_fetcher
import data_analyzer
import locations

def process_location(location_data, location_index):
    """
    Process a single location's data and assess boating conditions.
    
    Args:
        location_data (dict): Location data dictionary
        location_index (int): Index of the location in the list
        
    Returns:
        tuple: (location_name, results_dict)
    """
    print(f"Processing location: {location_data['name']}, {location_data['region']}")
    
    # Get location info for sunrise/sunset calculations
    location_info = data_analyzer.get_location_info(location_data)
    
    # Fetch weather and marine data
    weather_df = data_fetcher.fetch_weather_data(
        location_data["latitude"], 
        location_data["longitude"]
    )
    
    marine_df = data_fetcher.fetch_marine_data(
        location_data["latitude"], 
        location_data["longitude"]
    )
    
    # Analyze conditions for this location
    results = data_analyzer.analyze_conditions(marine_df, weather_df, location_info)
    
    return location_data['name'], results

def analyze_all_locations():
    """
    Process all locations and return their boating conditions.
    
    Returns:
        dict: All boating conditions for all locations
    """
    all_results = {}
    
    # Process each location
    for i, location in enumerate(locations.LOCATIONS):
        location_name, results = process_location(location, i)
        all_results[location_name] = results
    
    return all_results

def run_analysis():
    """
    Run the full analysis and return results.
    
    Returns:
        tuple: (all_results, good_days_results)
    """
    # Get forecast data for all locations
    all_results = analyze_all_locations()
    
    # Filter for good days
    good_days_results = data_analyzer.find_good_days(all_results)
    
    return all_results, good_days_results

def save_results_to_files(all_results, good_days_results):
    """
    Save analysis results to JSON and HTML files.
    
    Args:
        all_results (dict): All boating conditions results
        good_days_results (dict): Filtered good days results
    """
    # Save full results to JSON (will overwrite existing file)
    with open("all_boating_conditions.json", 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Save good days to JSON (will overwrite existing file)
    with open("good_boating_days.json", 'w') as f:
        json.dump(good_days_results, f, indent=2)
    
    # Generate HTML table for all days (will overwrite existing file)
    html_content = table_generation.generate_html_tables(all_results)
    with open("all_boating_conditions.html", "w") as f:
        f.write(html_content)
        
    print("\nHTML report generated: all_boating_conditions.html")
    
    # Try to open the HTML file in browser
    try:
        file_path = os.path.abspath("all_boating_conditions.html")
        webbrowser.open('file://' + file_path)
        print(f"Opened HTML report in browser")
    except Exception as e:
        print(f"Could not open HTML file automatically. Please open it manually: {e}")

def print_summary(all_results, good_days_results):
    """
    Print a summary of the analysis results to the console.
    
    Args:
        all_results (dict): All boating conditions results
        good_days_results (dict): Filtered good days results
    """
    print("\nBoating Conditions Summary:")
    
    # Print all results summary
    for location_name, location_results in all_results.items():
        print(f"\n=== {location_name} ===")
        for date, data in location_results.items():
            print(f"\n{date}: {data['day_rating']}")
            print(f"  Sunrise: {data['sunrise']}, Sunset: {data['sunset']}")
            print(f"  Good hours: {data['good_hours_count']}")
            
            # Print sample hourly ratings
            print("  Sample hourly ratings:")
            for i, hour in enumerate(data['hourly'][:3]):
                print(f"    {hour['time']}: {hour['rating']} - Wave: {hour['wave_height_ft']}ft, Wind: {hour['wind_speed_mph']}mph")
            if len(data['hourly']) > 3:
                print(f"    ... and {len(data['hourly']) - 3} more hours")
    
    # Print good days summary
    if good_days_results:
        print("\n\n=== GOOD BOATING DAYS ===")
        for location_name, good_days in good_days_results.items():
            print(f"\n{location_name}:")
            for date, data in good_days.items():
                # Calculate time range
                good_hours = data['hourly']
                if good_hours:
                    first_good_hour = good_hours[0]['time']
                    last_good_hour = good_hours[-1]['time']
                    time_range = f"{first_good_hour} - {last_good_hour}"
                    print(f"  {date}: {data['day_rating']} - {len(good_hours)} good hours ({time_range})")
                else:
                    print(f"  {date}: {data['day_rating']} - 0 good hours")

def get_current_date():
    """
    Return the current date as a formatted string.
    
    Returns:
        str: Current date in YYYY-MM-DD format
    """
    return datetime.now().strftime("%Y-%m-%d")

def main():
    """Main function to run the entire forecasting process."""
    # No need to explicitly delete files as we'll overwrite them
    
    # Run analysis
    all_results, good_days_results = run_analysis()
    
    # Save results to files (overwrites existing files)
    save_results_to_files(all_results, good_days_results)
    
    # Print summary to console
    print_summary(all_results, good_days_results)

if __name__ == "__main__":
    main() 