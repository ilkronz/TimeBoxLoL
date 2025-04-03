# TimeBoxLoL
Fix your League of Legends addiction (Windows only)

# Features
- Timeboxes usage it between 9:00 PM and 1:00 AM
- When you try to launch it anytime outside of that, it kills the process and gives you a "Get to work!" popup

# Requirements
- Python
- psutil (pip install psutil)

# Installation
- Download/clone the repo
- 'Open Task Scheduler' > 'Create Basic Task' > 'Name/Description' however you like
- 'Trigger': "When I log on" > 'Action': "Start a program"
- 'Program/script': Find your local Pythonw.exe path and copy/paste it here
- 'Add arguments': Find your local path to the lol_blocker.py and copy/paste it here
- 'Start in": Find your local path to the folder containing lol_blocker.py and copy/paste it here
- Next/Finish
- Go to Task Scheduler library > right click the blocker > select properties
- On the Conditions tab uncheck options like "Start the task only if the computer is on AC" and stuff
- Restart your computer
- Congrats