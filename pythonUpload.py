#!/usr/bin/python3
import sys
import os
import requests
from PIL import Image, ImageFilter, PngImagePlugin
import json
import base64

def check_image_for_nudity(image_path, api_user, api_secret):
    # Make API request
    url = 'https://api.sightengine.com/1.0/check.json'
    files = {'media': open(image_path, 'rb')}
    data = {'models': 'nudity-2.1', 'api_user': api_user, 'api_secret': api_secret}
    response = requests.post(url, files=files, data=data)
    
    # Parse response
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to check image")
        return None

def process_nudity_data(data):
    if data['nudity']['none'] > 0.6:
        print("Looking Good")
        send_email = True #TODO Change back to false
        send_text = False
    else:
        send_email = True
        if (data['nudity']['sexual_activity'] > 0.5 or 
            data['nudity']['sexual_display'] > 0.5 or 
            data['nudity']['erotica'] > 0.5):
            print("Really Bad")
            send_text = True
        elif (data['nudity']['suggestive'] > 0.5 or 
              data['nudity']['mildly_suggestive'] > 0.7 or 
              data['nudity']['very_suggestive'] > 0.5):
            print("Kinda Bad")
            send_text = False
    return send_email, send_text

#def blur_image(image_path, nudity_data):
#    img = Image.open(image_path)
#    blurred_img = img.filter(ImageFilter.GaussianBlur(20))  # Apply blur twice for a stronger effect
#    blurred_img.save('/tmp/Blurred.png')
#    nudity_data_str = json.dumps(nudity_data)
#    img = Image.open("/tmp/Blurred.png")
#    metadata = PngImagePlugin.PngInfo()
#    metadata.add_text("Nudity_Info", nudity_data_str)
#    img = img.resize((img.width // 2, img.height //2))
#    img.save("/tmp/Blurred.png", pnginfo=metadata)
def blur_image(image_path, nudity_data):
    # Open the image
    img = Image.open(image_path)
    
    # Apply a Gaussian blur to the image
    blurred_img = img.filter(ImageFilter.GaussianBlur(20))
    
    # Resize the image to 50% of its original dimensions
    blurred_img = blurred_img.resize((blurred_img.width // 2, blurred_img.height // 2))
    
    # Convert the nudity data to a JSON string
    nudity_data_str = json.dumps(nudity_data)
    
    # Create a PngInfo object to hold the metadata
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Nudity_Info", nudity_data_str)
    
    # Save the image with the added metadata
    blurred_img.save("/tmp/Blurred.png", pnginfo=metadata)


def upload_image(image_path, server_url, auth_key):
    # URL of the webhook server
    url = "https://odinforce.net/hooks/upload-data?token=PWatch"
    #url = "http://penguinwatch.odinforce.net:9000/hooks/upload-data?token=PWatch"

    # String data to send
    text_data = "Hello, this is a test string."

    # Read and encode the image as base64
    with open("/tmp/Blurred.png", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Prepare the payload
    payload = {
        "text": text_data,
        "image_data": encoded_image
    }
    #print(payload)

    # Send POST request
    response = requests.post(url, json=payload)

    # Print the response
    print(response.text)

def send_notifications(send_email, send_text):
    if send_email:
        # Send an email notification
        server_url = 'http://.odinforce.net/hooks/upload'  # Replace with your server URL
        #server_url = 'http://penguinwatch.odinforce.net:9000/hooks/upload'
        auth_key = 'EXAMPLE-1234-5678'  # Replace with your actual auth key
        upload_image(image_path, server_url, auth_key)
        print("Email sent with blurred image")
        # Add code to send an email

    if send_text:
        # Send a text notification
        print("Text sent about image")
        # Add code to send a text message

# Placeholder values
image_path = '/tmp/screenshot.png'
#Get API and User Info from File
config = {}
with open('/opt/PenguinWatch/config.txt') as file:
    for line in file:
        if line.strip() and not line.startswith("#"):
    	    key, value = line.strip().split('=', 1)
    	    config[key] = value
api_user = config.get('SE_user')
api_secret = config.get('SE_secret')
UserName = config.get('PWUser')

# Check if a file path is provided as a command-line argument
if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    file_path = '/tmp/screenshot.png'

if not os.path.exists(file_path):
   print(f"Error: File does not exist: {file_path}")
   sys.exit(1)

# Check the image for nudity
nudity_data = check_image_for_nudity(file_path, api_user, api_secret)
if nudity_data:
    #Encode the data into the photo for troubleshooting
    #nudity_data_str = json.dumps(nudity_data)
    #img = Image.open("/tmp/screenshot.png")
    #metadata = PngImagePlugin.PngInfo()
    #metadata.add_text("Nudity_Info", nudity_data_str)
    #img.save("/tmp/screenshot.png", pnginfo=metadata)
    # Process nudity data and decide actions
    send_email, send_text = process_nudity_data(nudity_data)
    
    # If an email should be sent, blur the image
    if send_email:
        blur_image(image_path, nudity_data)
    
    # Send notifications
    send_notifications(send_email, send_text)
