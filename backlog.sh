#!/bin/bash

# URL to check
URL="https://odinforce.net/hooks/webhook-monitor"

# Directory to check for numbered files
DIR="/opt/PenguinWatch/hold"

# Use curl to get the response
RESPONSE=$(curl -s $URL)

# Check if the response contains the expected string
if [[ "$RESPONSE" == "webhook is running" ]]; then
  echo "Webhook is running."

  # Loop through numbered files in the directory
  for FILE in "$DIR"/*.png; do
    # Check if there are no files matching the pattern
    if [[ ! -e $FILE ]]; then
      echo "No numbered files found in $DIR."
      break
    fi

    # Perform your desired action on each file
    # Example action: print the filename
    echo "Processing $FILE"
    /opt/PenguinWatch/pythonUpload.py $FILE
    # Add your actual action here, such as uploading the file
    # Example: curl -X POST -F "file=@$FILE" http://yourserver/upload

    # Remove or archive the file after processing
    rm "$FILE"  # Uncomment to delete the file after processing
    # mv "$FILE" /path/to/archive/  # Uncomment to move the file to an archive directory
  done

else
  echo "Webhook is not running. Skipping file processing."
fi
