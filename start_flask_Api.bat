@echo off
REM Go to the Automated-Job-Tracker folder
cd /d "C:\Users\Haider Ali Shahid\OneDrive\Desktop\Job_Tracker\Automated-Job-Tracker"

REM Start Flask silently using pythonw (global), running python.exe from env
start "" "C:\Users\Haider Ali Shahid\anaconda3\pythonw.exe" "C:\Users\Haider Ali Shahid\anaconda3\envs\jobtracker\python.exe" flask_api.py"

exit
