#Lambda Function to catch reports
import json
import os
import base64
import smtplib
import logging
import requests
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from PIL import Image, ImageFilter
import boto3

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
#logging.info("Test Info Message")
#logging.warning("Test Warning Message")
#logging.error("Test Error")

# Set up SES Client
ses_client = boto3.client('ses', region_name='us-east-1')

'''
# SMTP configuration (replace these with your actual values)
SMTP_SERVER = 'mail.example.net'
SMTP_PORT = 587
FROM_EMAIL = 'noreply@example.net'
PASSWORD = 'YourPassword'
'''

def save_image_file(image_data_base64, file_path):
    """Save base64-encoded image data to a file."""
    logging.info(f"Saving image to {file_path}...")
    try:
        image_data = base64.b64decode(image_data_base64)
        with open(file_path, "wb") as image_file:
            image_file.write(image_data)
        logging.info(f"Image saved successfully at {file_path}.")
    except Exception as e:
        logging.error(f"Failed to save image: {e}")

def send_email(subject, body_plain, body_html, to_email, image_path, bad_words):
    """Send an email with an image attachment using Amazon SES."""
    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = 'noreply@example.net'
    #msg['To'] = ''
    msg['To'] = ''

    # Create a multipart/alternative child container for text and HTML content.
    msg_body = MIMEMultipart('alternative')

    # Add the body content (plain text and HTML)
    # TODO: Add the bad words here (probably)
    textpart = MIMEText(body_plain, 'plain')
    htmlpart = MIMEText(body_html, 'html')

    # Attach parts into message container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Attach the multipart/alternative child container to the multipart/mixed parent container.
    msg.attach(msg_body)
    # Read the file content and attach it to the email
    try:
        with open(image_path, 'rb') as file:
            att = MIMEApplication(file.read())
            att.add_header('Content-Disposition', 'attachment', filename='blurred_image.png')
            msg.attach(att)
            logging.info(f"Attachment added: {image_path}")
    except Exception as e:
        logging.error(f"Failed to attach file: {e}")
        return False

    # Send the email using SES
    try:
        response = ses_client.send_raw_email(
            Source='noreply@example.net',
            Destinations=[
                'email1@example.net',
                'email2@example.net'
            ],
            RawMessage={
                'Data': msg.as_string()
            }
        )
        logging.info(f"Email sent! Message ID: {response['MessageId']}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def send_text(phoneNumber):
    message = """
Hello [Accountability Partner Name]
We detected some concerning content in the media recently viewed by [User Name]. Please reach out and provide support as needed.

Sincerely,
PenguinWatch
"""
    resp = requests.post('https://textbelt.com/text', {
        'phone': phoneNumber,
        'message': message,
        'key': 'textbelt',
})

def lambda_handler(event, context):
    """Main Lambda handler function."""
    sendEmailBool = False
    logging.info("Lambda function invoked.")
    logging.info(f"Event received: {json.dumps(event)}")

    try:
        # Log the body of the incoming request
        if 'body' in event:
            logging.info(f"Request body: {event['body']}")
        else:
            logging.error("No body in the request!")

        # Parse incoming data (JSON payload from API Gateway)
        data = json.loads(event.get('body', '{}'))
        logging.info(f"Parsed data: {data}")

        # Extract relevant data
        image_data_base64 = data.get('image_data')
        user_email = 'user@example.net'

        # Log the extracted data
        logging.info(f"Extracted image data: {bool(image_data_base64)}, User email: {user_email}")

        if not image_data_base64 or not user_email:
            logging.error("Invalid input: Missing image data or email.")
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid input: Missing image data or email.')
            }

        # Save the image to /tmp (Lambda's temporary storage)
        image_path = '/tmp/screenshot.png'
        save_image_file(image_data_base64, image_path)


        # Check for nudity in the image
        img = Image.open('/tmp/screenshot.png')
        nudity_info_str = img.info.get("Nudity_Info")
        bad_words_str   = img.info.get("BadWords")
        logging.warning(bad_words_str)
        if bad_words_str != "none":
            logging.warning("Bad_words_str != none")
            sendEmailBool = True
            bad_words = bad_words_str.split('_')
        else:
            logging.warning("Bad_words == none")
            bad_words = []
        if nudity_info_str:
            #Convert string back to json
            data = json.loads(nudity_info_str)
            if (data['nudity']['sexual_activity'] > 0.5 or 
                data['nudity']['sexual_display'] > 0.5 or 
                data['nudity']['erotica'] > 0.5):
                logging.info("Really Bad")
                
                # List of phone numbers
                phone_numbers = [
                    "1234567890",
                    "2345678901",
                    "3456789012"
                ]
                
                # Loop through each phone number
                for phone_number in phone_numbers:
                    send_text(phone_number)
                sendEmailBool = True
        
        #Build the Body
        bad_words_pretty = ", ".join(bad_words)
        if bad_words != []:
            logging.warning("Bad_words != []")
            body_plain = f"""
Hello,
We wanted to bring something to your attention. The person you hold accountable recently had a screenshot that our system flagged for review. Please find a blurred copy of the screenshot attached to this email.
We encourage you to take a moment to review the image and consider reaching out to your friend. They may need your support at this time.
This screenshot was flagged because of the window titled {bad_words_pretty}.
Thank you for being there for them.

Best regards,
The PenguinWatch Team
"""
            body_html = f"""
<html>
  <body>
    <p>Dear [Accountability Partner's Name],</p>
    <p>We wanted to bring something to your attention. The person you hold accountable recently had a screenshot that our system flagged for review. Please find a blurred copy of the screenshot attached to this email.</p>
    <p>We encourage you to take a moment to review the image and consider reaching out to your friend. They may need your support at this time.</p>
    <p><strong>This screenshot was flagged because of the window titled {bad_words_pretty}.</strong></p>
    <p>Thank you for being there for them.</p>
    <p>Best regards,<br>[Your Name or Program Name]</p>
"""
        else:
            logging.warning("Bad_words == []")
            body_plain = f"""
Hello,
We wanted to bring something to your attention. The person you hold accountable recently had a screenshot that our system flagged for review. Please find a blurred copy of the screenshot attached to this email.
We encourage you to take a moment to review the image and consider reaching out to your friend. They may need your support at this time.
Thank you for being there for them.

Best regards,
The PenguinWatch Team
"""
            body_html = f"""
<html>
  <body>
    <p>Dear [Accountability Partner's Name],</p>
    <p>We wanted to bring something to your attention. The person you hold accountable recently had a screenshot that our system flagged for review. Please find a blurred copy of the screenshot attached to this email.</p>
    <p>We encourage you to take a moment to review the image and consider reaching out to your friend. They may need your support at this time.</p>
    <p>Thank you for being there for them.</p>
    <p>Best regards,<br>The PenguinWatch Team</p>
  </body>
</html>
"""
        if (data['nudity']['suggestive'] > 0.5 or 
              data['nudity']['mildly_suggestive'] > 0.7 or 
              data['nudity']['very_suggestive'] > 0.5):
            sendEmailBool = True
        
        # Send the email with the processed image
        if sendEmailBool:
            send_email(
                subject="Concerning Content Detected - PenguinWatch",
                body_plain=body_plain,
                body_html=body_html,
                to_email=user_email,
                image_path=image_path,
                bad_words=bad_words
            )

        logging.info("Image processing complete.")
        return {
            'statusCode': 200,
            'body': json.dumps(f'Image processed successfully.')
        }

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }
