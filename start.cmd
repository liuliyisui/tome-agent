@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please run setup.cmd first.
  pause
  exit /b 1
)
set "PYTHONPATH=%~dp0code\core_engine;%~dp0code\backend;%PYTHONPATH%"
".venv\Scripts\python.exe" -m streamlit run code\frontend\app.py --server.address 127.0.0.1
