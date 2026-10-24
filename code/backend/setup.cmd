@echo off
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 exit /b 1
if not exist ".env" copy ".env.example" ".env" >nul
echo Setup complete. INF uses the Python standard library.
echo Run run-web.cmd to start the writing studio.
pause
