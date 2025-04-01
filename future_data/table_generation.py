import pandas as pd
import os

def export_to_excel(good_days_results, filename="good_boating_days.xlsx"):
    """
    Export good boating days to a nicely formatted Excel file with tables
    for each location.
    
    Args:
        good_days_results (dict): Dictionary of location names to good boating days data
        filename (str): Name of the Excel file to create
    
    Returns:
        str: Path to the created Excel file
    """
    # Create a Pandas Excel writer
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    workbook = writer.book
    
    # Add a title format
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#D0E0F0',
        'border': 1
    })
    
    # Add header format
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#E0E0E0',
        'border': 1
    })
    
    # Add data formats
    date_format = workbook.add_format({
        'num_format': 'yyyy-mm-dd',
        'align': 'center',
        'border': 1
    })
    
    time_format = workbook.add_format({
        'align': 'center',
        'border': 1
    })
    
    number_format = workbook.add_format({
        'num_format': '0.0',
        'align': 'center',
        'border': 1
    })
    
    rating_format_good = workbook.add_format({
        'align': 'center',
        'bg_color': '#C6EFCE',  # Light green
        'border': 1,
        'bold': True
    })
    
    # Process each location
    for location_name, good_days in good_days_results.items():
        # Create a DataFrame to hold all hourly data for this location
        all_hours_data = []
        
        for date, data in good_days.items():
            good_hours = data['hourly']
            for hour in good_hours:
                all_hours_data.append({
                    'Date': date,
                    'Time': hour['time'],
                    'Wave Height (ft)': hour['wave_height_ft'],
                    'Wind Speed (mph)': hour['wind_speed_mph'],
                    'Wind Gust (mph)': hour['wind_gust_mph'],
                    'Wave Period (sec)': hour['wave_period_sec'],
                    'Precip. Prob. (%)': hour['precipitation_probability'],
                    'Rating': hour['rating']
                })
        
        if not all_hours_data:
            continue  # Skip if no data
            
        # Create DataFrame and write to Excel
        df = pd.DataFrame(all_hours_data)
        
        # Create a sheet for each location (truncate name if too long)
        sheet_name = location_name[:31]  # Excel sheet names limited to 31 chars
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
        
        # Get the worksheet object
        worksheet = writer.sheets[sheet_name]
        
        # Write the column headers with the header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Set column widths
        worksheet.set_column('A:A', 12)  # Date
        worksheet.set_column('B:B', 10)  # Time
        worksheet.set_column('C:C', 14)  # Wave Height
        worksheet.set_column('D:D', 14)  # Wind Speed
        worksheet.set_column('E:E', 14)  # Wind Gust
        worksheet.set_column('F:F', 14)  # Wave Period
        worksheet.set_column('G:G', 14)  # Precip Prob
        worksheet.set_column('H:H', 10)  # Rating
        
        # Apply formats
        for i, row in enumerate(df.iterrows()):
            row_idx = i + 1  # Adjusted for header
            
            # Apply conditional formatting based on rating
            rating = row[1]['Rating']
            if rating == 'GOOD':
                worksheet.write(row_idx, 7, rating, rating_format_good)
            
            # Set date format
            worksheet.write(row_idx, 0, row[1]['Date'], date_format)
            
            # Set number formats
            for col in [2, 3, 4, 5, 6]:  # Columns with numeric values
                worksheet.write(row_idx, col, row[1].iloc[col], number_format)
            
            # Set time format
            worksheet.write(row_idx, 1, row[1]['Time'], time_format)
        
        # Add a title for the sheet
        worksheet.merge_range('A1:H1', f"Good Boating Conditions - {location_name}", title_format)
    
    # Save the Excel file
    writer.close()
    print(f"Excel file saved: {filename}")
    return filename

def generate_html_tables(all_results):
    """
    Generate HTML tables for email with times in rows and dates in columns.
    Show all hours (24 hour day) and all condition types with color coding.
    
    Args:
        all_results (dict): Dictionary of location names to all boating days data
        
    Returns:
        str: HTML string with all tables
    """
    # Define HTML styles
    styles = """
    <style>
        table {
            border-collapse: collapse;
            margin-bottom: 20px;
            width: 100%;
        }
        th {
            background-color: #f2f2f2;
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        h2 {
            margin-top: 30px;
            color: #003366;
        }
        .good {
            background-color: #C6EFCE;
            font-weight: bold;
        }
        .great {
            background-color: #70AD47;
            font-weight: bold;
            color: white;
        }
        .mediocre {
            background-color: #FFEB9C;
            font-weight: bold;
        }
        .bad {
            background-color: #FFC7CE;
            color: #9C0006;
        }
    </style>
    """
    
    # Start HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        {styles}
    </head>
    <body>
        <h1>Boating Conditions Report</h1>
    """
    
    # Process each location
    for location_name, days_data in all_results.items():
        if not days_data:
            continue
            
        html += f"<h2>{location_name}</h2>"
        
        # Get all unique dates
        all_dates = sorted(days_data.keys())
        
        if not all_dates:
            html += "<p>No data found.</p>"
            continue
            
        # Create the table
        html += "<table>"
        
        # Header row with dates in MM-DD-YYYY format
        html += "<tr><th>Time</th>"
        for date in all_dates:
            # Convert date from YYYY-MM-DD to MM-DD-YYYY
            parts = date.split('-')
            formatted_date = f"{parts[1]}-{parts[2]}-{parts[0]}"
            html += f"<th>{formatted_date}</th>"
        html += "</tr>"
        
        # Create a lookup for quick access to data
        data_lookup = {}
        for date, date_data in days_data.items():
            for hour in date_data['hourly']:
                key = (date, hour['time'])
                data_lookup[key] = {
                    'rating': hour['rating'],
                    'day_rating': date_data['day_rating']
                }
        
        # Add rows for each hour (0-23)
        for hour in range(24):
            time_str = f"{hour:02d}:00"
            html += f"<tr><td><b>{time_str}</b></td>"
            
            for date in all_dates:
                key = (date, time_str)
                if key in data_lookup:
                    data = data_lookup[key]
                    rating = data['rating']
                    
                    # Determine CSS class based on rating
                    if rating == "GOOD":
                        css_class = "good"
                    elif rating == "GREAT":
                        css_class = "great"
                    elif rating == "MEDIOCRE":
                        css_class = "mediocre"
                    else:  # BAD
                        css_class = "bad"
                        
                    html += f"<td class='{css_class}'>{rating}</td>"
                else:
                    html += "<td></td>"  # Empty cell if no data
                    
            html += "</tr>"
            
        html += "</table>"
    
    html += """
    </body>
    </html>
    """
    
    return html

def create_summary_table(good_days_results):
    """
    Create a summary table of good boating days with accurate time ranges per location.
    """
    summary_data = []
    
    for location_name, good_days in good_days_results.items():
        for date, data in good_days.items():
            good_hours = data['hourly']
            if good_hours:
                # Find consecutive hour groups
                hour_groups = []
                current_group = [good_hours[0]]
                
                # Parse hours to integers for comparison
                for i in range(1, len(good_hours)):
                    prev_hour = int(good_hours[i-1]['time'].split(':')[0])
                    curr_hour = int(good_hours[i]['time'].split(':')[0])
                    
                    # Check if hours are consecutive
                    if curr_hour == prev_hour + 1:
                        current_group.append(good_hours[i])
                    else:
                        # Start a new group
                        hour_groups.append(current_group)
                        current_group = [good_hours[i]]
                
                # Add the last group
                hour_groups.append(current_group)
                
                # Format time ranges for each group
                time_ranges = []
                for group in hour_groups:
                    if len(group) == 1:
                        time_ranges.append(f"{group[0]['time']}")
                    else:
                        time_ranges.append(f"{group[0]['time']} - {group[-1]['time']}")
                
                time_range_str = ", ".join(time_ranges)
                
                # Add entry to summary data
                summary_data.append({
                    'Location': location_name,
                    'Date': date,
                    'Rating': data['day_rating'],
                    'Good Hours': len(good_hours),
                    'Time Ranges': time_range_str,
                    'Avg Wave Height (ft)': sum(h['wave_height_ft'] for h in good_hours) / len(good_hours),
                    'Avg Wind Speed (mph)': sum(h['wind_speed_mph'] for h in good_hours) / len(good_hours)
                })
    
    if not summary_data:
        return pd.DataFrame()
        
    # Create and return summary DataFrame
    return pd.DataFrame(summary_data)