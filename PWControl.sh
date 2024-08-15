#!/bin/bash

# Name of the script to check
SCRIPT_NAME="PenguinWatch.sh"

# Check if the script is running
if pgrep -f "$SCRIPT_NAME" > /dev/null; then
    echo "$(date): $SCRIPT_NAME is running."
else
    echo "$(date): $SCRIPT_NAME is not running."

    #Gather Env Variables
    USER=rhys
    DISPLAY=$(loginctl show-session $(loginctl | grep $USER | awk '{print $1}') -p Display | cut -d'=' -f2)
    DISPLAY=$(echo "$DISPLAY" | xargs | tr -d '\n')
    echo "DISPLAY=$DISPLAY"
    #Export the variables
    export DISPLAY=$DISPLAY
    export XAUTHORITY=$XAUTHORITY
    # Optionally, start the script if it's not running
    sudo -u rhys /opt/PenguinWatch/$SCRIPT_NAME "$DISPLAY" "$XAUTHORITY" 
fi
