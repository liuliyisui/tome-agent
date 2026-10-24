@echo off
setlocal
cd /d "%~dp0\..\.."
if not exist "code\backend\.venv\Scripts\python.exe" (
  echo Please run code\backend\setup.cmd first.
  exit /b 1
)
"code\backend\.venv\Scripts\python.exe" -m ensurepip --upgrade
if errorlevel 1 exit /b 1
"code\backend\.venv\Scripts\python.exe" -m pip install -r code\backend\requirements-build.txt
if errorlevel 1 exit /b 1
"code\backend\.venv\Scripts\python.exe" -m PyInstaller --noconfirm --workpath code\backend\data\build --distpath code\backend\data\dist code\backend\TomeAgent.spec
if errorlevel 1 exit /b 1
"code\backend\.venv\Scripts\python.exe" code\backend\package_windows.py
exit /b %errorlevel%
