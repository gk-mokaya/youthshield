@echo off
REM Batch file to run Django auto backup command
REM This file should be scheduled with Windows Task Scheduler

REM Set the path to your Django project directory
set PROJECT_DIR=%~dp0

REM Activate virtual environment if using one
REM Uncomment and modify the next line if you have a virtual environment
REM call %PROJECT_DIR%venv\Scripts\activate.bat

REM Change to project directory
cd /d %PROJECT_DIR%

REM Run the backup command
python manage.py auto_backup

REM Log the execution
echo Backup command executed at %date% %time% >> backup_log.txt

pause
