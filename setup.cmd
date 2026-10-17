@echo off
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements-lock.txt
if errorlevel 1 exit /b 1
if not exist ".env" copy ".env.example" ".env" >nul
echo Setup complete. Fill in .env, then run start.cmd.
pause
