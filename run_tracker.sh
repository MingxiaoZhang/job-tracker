#!/bin/bash
# Script to run the job tracker (for cron)

# Change to the tracker directory
cd /home/michaelz524/tracker

# Activate virtual environment and run tracker
source venv/bin/activate
python src/main.py >> logs/tracker.log 2>&1

# Exit with success
exit 0
