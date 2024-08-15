# PenguinWatch
Covenant Eyes like screen accountability for Linux

## Basic Structure
- PWControl.sh runs in the root crontab to verify PenguinWatch.sh is running. It starts it as the user if needed
- PenguinWatch.sh spend most of it's time sleeping for a random number about 5 minutes and triggering screenshot.sh
- Screenshot.sh takes a screenshot, decides if it can upload it right now, and either calls pythonUpload.py or saves it to a folder for processing later.
- PythonUpload evalutes the screenshot and if necessary, uploads it to the server for reporting.
- Eventually I want to add a daily report



# Tasks
- [X] Basic Bones
- [X] Root cron process can cause screenshots to be saved
- [ ] Only take screenshots if there  is a logged in user
- [ ] Embed the JSON data in the image for troubleshooting false positives
- [ ] Detect black screens where the user may have found a way to prevent screenshots
- [ ] Add exception handling.
- [ ] Add monitoring for notifications when the service has been down.
