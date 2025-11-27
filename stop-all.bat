@echo off
echo Stopping all GdeDoctor services...

echo Stopping Python processes...
taskkill /f /im python.exe 2>nul

echo Stopping uvicorn processes...
taskkill /f /im uvicorn.exe 2>nul

echo.
echo ✓ All services stopped
pause
