@echo off
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 exit /b 1
if not exist ".env" copy ".env.example" ".env" >nul
echo Setup complete. INF uses the Python standard library.
echo Run run-demo.cmd for the offline four-agent demo.
pause
