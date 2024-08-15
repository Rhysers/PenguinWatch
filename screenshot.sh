#!/bin/bash
export DISPLAY=$1
export XAUTHORITY=$2
rm /tmp/screenshot.png 2> /dev/null
flameshot full --path  /tmp/screenshot.png > /dev/null


# URL to check
URL="https://odinforce.net/hooks/webhook-monitor"

# Use curl to get the response
RESPONSE=$(curl -s $URL)

# Check if the response contains the expected string
if [[ "$RESPONSE" == "webhook is running" ]]; then
  echo "Webhook is running."
  /opt/PenguinWatch/pythonUpload.py
else
  echo "Webhook is not running."
  # Add actions to take if the response is not as expected

  # Directory to move the screenshot to
  DEST_DIR="/opt/PenguinWatch/hold"

  # Check if the directory exists, and create it if it doesn't
  if [ ! -d "$DEST_DIR" ]; then
    mkdir -p "$DEST_DIR"
  fi
  #find the number of the next pending file
  COUNT=1
  while [ -e "$DEST_DIR/$COUNT.png" ]; do
    ((COUNT++))
  done

  # Move and rename the screenshot
  mv "/tmp/screenshot.png" "$DEST_DIR/$COUNT.png" #TODO Add sudo here, after setting up the sudoers file
  echo "Moved screenshot.png to $DEST_DIR/$COUNT.png"
fi
