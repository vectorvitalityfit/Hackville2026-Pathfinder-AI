@echo off
REM Quick start script for phone camera setup

echo ================================================
echo   Voice Navigation - Phone Camera Setup
echo ================================================
echo.

echo Step 1: Make sure IP Webcam is running on your phone
echo   - Open IP Webcam app
echo   - Tap "Start server"
echo   - Note the URL shown
echo.

set /p phone_ip="Enter your phone's IP address (e.g., 192.168.1.105): "

if "%phone_ip%"=="" (
    echo Error: No IP address entered
    pause
    exit /b
)

echo.
echo Updating client_orchestrator.py with phone IP: %phone_ip%
echo.

REM Update the CAMERA_URL in client_orchestrator.py
powershell -Command "(Get-Content client_orchestrator.py) -replace 'CAMERA_URL = 0', 'CAMERA_URL = \"http://%phone_ip%:8080/video\"' | Set-Content client_orchestrator.py"

echo Configuration updated!
echo.

echo Testing connection to phone camera...
echo Opening http://%phone_ip%:8080 in browser...
start http://%phone_ip%:8080

timeout /t 3 >nul

echo.
echo If you see the camera feed in your browser, the connection works!
echo.
echo ================================================
echo   Ready to Start System
echo ================================================
echo.
echo Terminal 1 (Backend):
echo   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
echo.
echo Terminal 2 (Client):
echo   python client_orchestrator.py
echo.
echo Press any key to close this window...
pause >nul
