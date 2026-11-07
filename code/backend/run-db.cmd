@echo off
cd /d "%~dp0"
docker compose up -d --wait
if errorlevel 1 exit /b 1
echo PostgreSQL is ready on 127.0.0.1:5432.
