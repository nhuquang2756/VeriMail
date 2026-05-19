@echo off
REM Setup config.json from example

echo Creating config.json from example...

if exist "config\config.json" (
    echo WARNING: config.json already exists!
    set /p confirm="Do you want to overwrite it? (y/N): "
    if /i not "%confirm%"=="y" (
        echo Cancelled.
        exit /b 1
    )
)

copy "config\config.example.json" "config\config.json"

echo.
echo ========================================
echo ✅ config.json created!
echo ========================================
echo.
echo 📝 Please edit config\config.json and add:
echo    - Your Gmail address
echo    - Your App Password (16 characters)
echo    - (Optional) Telegram bot token and chat ID
echo.
echo 💡 To get Gmail App Password:
echo    1. Go to https://myaccount.google.com/apppasswords
echo    2. Create a new app password
echo    3. Copy the 16-character password
echo.
pause
