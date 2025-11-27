@echo off
echo Installing GdeDoctor project dependencies for Windows...

echo.
echo Installing backend dependencies...
cd backend
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo.
echo Installing bot dependencies...
cd bot
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo.
echo All dependencies installed successfully!
echo.
echo To run the project:
echo   - Backend: run-backend.bat
echo   - Bot: run-bot.bat
echo   - Both: run-dev.bat
pause