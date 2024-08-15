#!/bin/bash

# Path to the script to be triggered
SCRIPT_PATH="/opt/PenguinWatch/screenshot.sh"
Disp=$1
XAuth=$2
echo "Display is $Disp"
# Infinite loop to repeatedly trigger the script
while true; do
    # Generate a random number between 240 and 360
    INTERVAL=$((RANDOM % 121 + 240))
    #INTERVAL=20
    # Log the interval (optional, useful for debugging)
    echo "Next execution in $INTERVAL seconds."
    
    # Wait for the random interval
    sleep $INTERVAL
    
    # Trigger the script
    if [ -x "$SCRIPT_PATH" ]; then
        $SCRIPT_PATH $1 $2
    else
        echo "Error: $SCRIPT_PATH is not executable or not found."
        exit 1
    fi
done
