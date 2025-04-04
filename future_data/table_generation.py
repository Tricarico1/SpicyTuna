import pandas as pd
import os
from datetime import datetime

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
    Merges consecutive hours with the same condition rating vertically.
    
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
            font-family: Arial, sans-serif;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
            position: sticky;
            top: 0;
        }
        .good {
            background-color: #c8e6c9;  /* light green */
            font-weight: bold;
            border: 2px solid #000000;  /* bold black border */
        }
        .mediocre {
            background-color: #fff9c4;  /* light yellow */
            font-weight: bold;
            border: 2px solid #000000;  /* bold black border */
        }
        .bad {
            background-color: #ffcdd2;  /* light red */
            font-weight: bold;
            border: 2px solid #000000;  /* bold black border */
        }
        .location-header {
            background-color: #2196F3;
            color: white;
            font-size: 1.2em;
            padding: 10px;
            text-align: center;
            margin-top: 20px;
            margin-bottom: 5px;
            border-radius: 4px;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .hour-cell {
            font-weight: bold;
            background-color: #e0e0e0;
        }
        h1 {
            color: #2196F3;
            text-align: center;
        }
        .date-header {
            background-color: #e1f5fe;
            font-weight: bold;
        }
        .weekday {
            font-size: 0.8em;
            color: #555;
        }
        .hour-count {
            font-size: 0.8em;
            margin-top: 4px;
        }
    </style>
    """

    # Start HTML document
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Boating Conditions Forecast</title>
        {styles}
    </head>
    <body>
        <h1>Boating Conditions Forecast</h1>
    """

    # For each location
    for location_name, location_results in all_results.items():
        # Add location header
        html += f"<div class='location-header'>{location_name}</div>"
        
        # Create a table for this location
        html += "<table>"
        
        # Get all dates for columns
        dates = sorted(location_results.keys())
        
        if not dates:
            html += "<tr><td>No data available for this location.</td></tr></table>"
            continue
        
        # Add header row with dates and weekdays
        html += "<tr><th>Hour</th>"
        for date in dates:
            # Format date from YYYY-MM-DD to MM/DD
            formatted_date = f"{date[5:7]}/{date[8:10]}"
            
            # Get day of week
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            weekday = date_obj.strftime("%A")
            
            html += f"<th class='date-header'>{formatted_date}<br><span class='weekday'>{weekday}</span></th>"
        html += "</tr>"
        
        # Pre-process to find vertical blocks for each date
        date_blocks = {}
        
        for date in dates:
            if date not in location_results:
                date_blocks[date] = []
                continue
                
            # Get all hourly data sorted by time
            hourly_data = sorted(
                location_results[date].get('hourly', []),
                key=lambda x: x['time']
            )
            
            if not hourly_data:
                date_blocks[date] = []
                continue
                
            # Find blocks of consecutive hours with the same rating
            blocks = []
            current_block = {
                'rating': hourly_data[0]['rating'],
                'start_hour': hourly_data[0]['time'],
                'end_hour': hourly_data[0]['time'],
                'count': 1
            }
            
            for i in range(1, len(hourly_data)):
                current_hour = hourly_data[i]
                prev_hour = hourly_data[i-1]
                
                # Check if current hour is consecutive to previous hour and has same rating
                prev_hour_int = int(prev_hour['time'].split(':')[0])
                curr_hour_int = int(current_hour['time'].split(':')[0])
                
                if curr_hour_int == prev_hour_int + 1 and current_hour['rating'] == current_block['rating']:
                    # Extend the current block
                    current_block['end_hour'] = current_hour['time']
                    current_block['count'] += 1
                else:
                    # End current block and start a new one
                    blocks.append(current_block)
                    current_block = {
                        'rating': current_hour['rating'],
                        'start_hour': current_hour['time'],
                        'end_hour': current_hour['time'],
                        'count': 1
                    }
            
            # Add the last block
            blocks.append(current_block)
            date_blocks[date] = blocks
        
        # Get all possible hours (00:00 to 23:00)
        all_hours = [f"{h:02d}:00" for h in range(24)]
        
        # Build the table row by row
        for hour_idx, hour in enumerate(all_hours):
            html += f"<tr><td class='hour-cell'>{hour}</td>"
            
            # Process each date column
            for date in dates:
                # Find if this hour is the start of a block
                is_start_of_block = False
                matching_block = None
                
                for block in date_blocks.get(date, []):
                    if block['start_hour'] == hour:
                        is_start_of_block = True
                        matching_block = block
                        break
                
                # Check if this hour is in the middle of a block (should be skipped)
                is_in_middle_of_block = False
                if not is_start_of_block:
                    for block in date_blocks.get(date, []):
                        start_hour_int = int(block['start_hour'].split(':')[0])
                        end_hour_int = int(block['end_hour'].split(':')[0])
                        current_hour_int = int(hour.split(':')[0])
                        
                        if start_hour_int < current_hour_int <= end_hour_int:
                            is_in_middle_of_block = True
                            break
                
                # Skip if in middle of block (already covered by rowspan)
                if is_in_middle_of_block:
                    continue
                
                # If start of block, create cell with rowspan
                if is_start_of_block and matching_block:
                    rating = matching_block['rating']
                    rowspan = matching_block['count']
                    
                    # Set CSS class based on rating
                    if rating == "GOOD":
                        css_class = "good"
                        # For GOOD ratings, display the hour count
                        cell_content = f"{rating}<br><span class='hour-count'>{rowspan} hr</span>"
                    elif rating == "MEDIOCRE":
                        css_class = "mediocre"
                        cell_content = rating
                    else:  # BAD
                        css_class = "bad"
                        cell_content = rating
                    
                    # Add cell with appropriate rowspan
                    html += f"<td class='{css_class}' rowspan='{rowspan}'>{cell_content}</td>"
                else:
                    # If no block starts here and not in middle of block, add empty cell
                    html += "<td></td>"
            
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