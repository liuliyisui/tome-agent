@echo off
cd /d "%~dp0\..\.."
if not exist "code\backend\.venv\Scripts\python.exe" (
  echo Please run code\backend\setup.cmd first.
  pause
  exit /b 1
)
set "PYTHONPATH=%CD%\code\core_engine;%CD%\code\backend;%PYTHONPATH%"
"code\backend\.venv\Scripts\python.exe" -m inf_writer demo --output code\backend\data\runs\offline-demo
pause
