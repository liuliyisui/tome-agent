@echo off
cd /d "%~dp0\..\.."
set "PYTHONPATH=%CD%\code\core_engine;%CD%\code\backend;%PYTHONPATH%"
if exist "code\backend\.venv\Scripts\python.exe" (
  "code\backend\.venv\Scripts\python.exe" -m inf_backend.web %*
) else (
  python -m inf_backend.web %*
)
