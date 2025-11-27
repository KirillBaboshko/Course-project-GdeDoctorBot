@echo off
echo Starting GdeDoctor Bot...
cd bot
call .venv\Scripts\activate
python -m app.main
pause