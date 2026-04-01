@echo off
cd /d "%~dp0"
python main_web.py
if errorlevel 1 (
    echo Failed to launch. Make sure Python 3.10+ is installed.
    pause
)
