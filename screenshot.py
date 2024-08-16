#!/usr/bin/python3
import os
import sys
import shutil
import subprocess
from PIL import Image
import requests

def take_screenshot(display, xauthority, screenshot_path="/tmp/screenshot.png"):
    os.environ['DISPLAY'] = display
#    os.environ['XAUTHORITY'] = xauthority
    
    # Remove the previous screenshot if it exists
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
    
    # Take a new screenshot
    subprocess.run(["flameshot", "full", "--path", screenshot_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def is_black_image(image_path, threshold=0.95):
    try:
        image = Image.open(image_path).convert('L')  # Convert to grayscale
        pixels = list(image.getdata())
        total_pixels = len(pixels)
        black_pixels = sum(1 for pixel in pixels if pixel == 0)  # Count black pixels
        
        black_ratio = black_pixels / total_pixels
        return black_ratio >= threshold
    except Exception as e:
        print(f"Error checking if image is black: {e}")
        return False

def check_webhook(url):
    try:
        response = requests.get(url)
        if response.status_code == 200 and "webhook is running" in response.text:
            return True
        return False
    except requests.RequestException as e:
        print(f"Error checking webhook: {e}")
        return False

def move_screenshot(src_path, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Find the next available filename
    count = 1
    while os.path.exists(os.path.join(dest_dir, f"{count}.png")):
        count += 1
    
    dest_path = os.path.join(dest_dir, f"{count}.png")
    
    # Move the screenshot
    shutil.move(src_path, dest_path)
    print(f"Moved {src_path} to {dest_path}")

def main():
    display = sys.argv[1]
#    xauthority = sys.argv[2]
    xauthority = None
    screenshot_path = "/tmp/screenshot.png"
    url = "https://odinforce.net/hooks/webhook-monitor"
    dest_dir = "/opt/PenguinWatch/hold"

    take_screenshot(display, xauthority, screenshot_path)
    
    if is_black_image(screenshot_path):
        print("The screenshot is mostly or entirely black.")
        move_screenshot(screenshot_path, dest_dir)
    elif check_webhook(url):
        print("Webhook is running.")
        # Run your Python script for uploading
        subprocess.run(["/opt/PenguinWatch/pythonUpload.py"])
    else:
        print("Webhook is not running.")
        move_screenshot(screenshot_path, dest_dir)

if __name__ == "__main__":
    main()

