"""
AWS Lambda handler for boating conditions forecast.
Generates and sends email with HTML tables of forecast.
"""
import json
import boto3
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('/tmp')  # Lambda needs to write to /tmp directory

# Import our modules directly (no need for future_data package prefix)
import future
import locations
import table_generation

def lambda_handler(event, context):
    """
    AWS Lambda entry point. Runs analysis and sends email.
    
    Args:
        event (dict): Lambda event data
        context (LambdaContext): Lambda context
        
    Returns:
        dict: Response with status code and message
    """
    try:
        # Ensure we're using /tmp for writable operations
        os.chdir('/tmp')
        
        # Run the weather analysis
        print("Starting weather analysis...")
        all_results = future.analyze_all_locations()
        
        # Generate HTML table for ALL days and conditions
        html_content = table_generation.generate_html_tables(all_results)
        
        # Send the email with just the HTML table
        send_email(html_content)
        
        return {
            'statusCode': 200,
            'body': 'Weather analysis complete, email sent!'
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def send_email(html_content):
    """
    Send email with forecast using AWS SES.
    
    Args:
        html_content (str): HTML content for email body
    """
    # Create message container
    msg = MIMEMultipart('alternative')
    
    # Create today's date for the subject line
    today = datetime.now().strftime("%m/%d/%Y")
    
    msg['Subject'] = f"Boating Conditions Report - {today}"
    msg['From'] = 'watershed.berks@gmail.com'
    msg['To'] = 'nathanieltricarico@gmail.com'
    
    # Attach HTML content to the email
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    # Create SES client
    ses = boto3.client('ses')
    
    # Print debug info
    print(f"Sending from: {msg['From']}")
    print(f"Sending to: {msg['To']}")
    
    # Send the email
    try:
        response = ses.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To']],
            RawMessage={'Data': msg.as_string()}
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return

# Optional function to save results to S3
# def save_to_s3(all_results, html_content):
#     try:
#         s3 = boto3.client('s3')
#         bucket_name = 'your-bucket-name'  # Replace with your S3 bucket name
        
#         # Save JSON results
#         s3.put_object(
#             Bucket=bucket_name,
#             Key='all_boating_conditions.json',
#             Body=json.dumps(all_results, indent=2),
#             ContentType='application/json'
#         )
        
#         # Save HTML file
#         s3.put_object(
#             Bucket=bucket_name,
#             Key='boating_conditions.html',
#             Body=html_content,
#             ContentType='text/html'
#         )
        
#         print("Files saved to S3 successfully")
#     except Exception as e:
#         print(f"Error saving to S3: {e}")

if __name__ == "__main__":
    # For local testing
    all_results = future.analyze_all_locations()
    
    # Save to JSON files
    with open("all_boating_conditions.json", 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Generate HTML for email preview
    html_content = table_generation.generate_html_tables(all_results)
    with open("boating_conditions.html", 'w') as f:
        f.write(html_content)
        
    # Open HTML in browser
    try:
        import webbrowser
        import os
        file_path = os.path.abspath("boating_conditions.html")
        webbrowser.open('file://' + file_path)
    except Exception as e:
        print(f"Could not open HTML file: {e}") 