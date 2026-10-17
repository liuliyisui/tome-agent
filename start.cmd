@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please run setup.cmd first.
  pause
  exit /b 1
)
set "PYTHONPATH=%~dp0code\core_engine;%~dp0code\backend;%PYTHONPATH%"
rem Local workbench settings; kept here so the repository root has no .streamlit folder.
set "STREAMLIT_SERVER_ADDRESS=127.0.0.1"
set "STREAMLIT_THEME_BASE=light"
set "STREAMLIT_THEME_PRIMARYCOLOR=#285943"
set "STREAMLIT_THEME_BACKGROUNDCOLOR=#FAF8F3"
set "STREAMLIT_THEME_SECONDARYBACKGROUNDCOLOR=#F0EDE5"
set "STREAMLIT_THEME_TEXTCOLOR=#242A26"
set "STREAMLIT_BROWSER_GATHERUSAGESTATS=false"
".venv\Scripts\python.exe" -m streamlit run code\frontend\app.py
