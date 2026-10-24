@echo off
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
if not exist ".env" copy ".env.example" ".env" >nul
echo Setup complete. See docs/software/POSTGRESQL.md for database setup.
echo Run run-web.cmd after starting PostgreSQL and migrating local books.
pause
