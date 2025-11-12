#!/bin/bash
# Script to run the job tracker (for cron)

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Activate virtual environment and run tracker
source venv/bin/activate
python tracker/src/main.py >> logs/tracker.log 2>&1

# Exit with success
exit 0
