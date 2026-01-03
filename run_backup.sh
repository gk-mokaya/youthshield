#!/bin/bash
# Shell script to run Django auto backup command
# This file should be scheduled with cron on Linux/Mac

# Set the path to your Django project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment if using one
# Uncomment and modify the next line if you have a virtual environment
# source $PROJECT_DIR/venv/bin/activate

# Change to project directory
cd $PROJECT_DIR

# Run the backup command
python manage.py auto_backup

# Log the execution
echo "Backup command executed at $(date)" >> backup_log.txt
