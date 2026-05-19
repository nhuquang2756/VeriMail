@echo off
echo.
echo ========================================
echo   Setup Gmail Config for AI Spam Detector
echo ========================================
echo.

REM Check if config.json already exists
if exist "config\config.json" (
    echo WARNING: config\config.json already exists!
    echo.
    set /p overwrite="Do you want to overwrite it? (y/N): "
    if /i not "%overwrite%"=="y" (
        echo.
        echo Cancelled. Opening existing config...
        notepad config\config.json
        exit /b 0
    )
)

REM Copy example to config
echo Copying config.example.json to config.json...
copy "config\config.example.json" "config\config.json" >nul

echo.
echo ========================================
echo SUCCESS: config.json created!
echo ========================================
echo.
echo Now opening config.json in Notepad...
echo Please edit the following fields:
echo   - "email": Your Gmail address
echo   - "password": Your Gmail App Password (16 chars)
echo.
echo Press any key to open config.json...
pause >nul

notepad config\config.json

echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo 1. Save the config.json file
echo 2. Run: python tray_launcher.py
echo 3. Click "Login Gmail" from tray menu
echo ========================================
echo.
pause
