@echo off
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -c "from pathlib import Path; root=Path.cwd(); (root/'.venv'/'Lib'/'site-packages'/'tome_agent_paths.pth').write_text('../../../code/core_engine\n../../../code/backend\n', encoding='ascii')"
if errorlevel 1 exit /b 1
echo Setup complete. Fill DEEPSEEK_API_KEY in .env, then run start.cmd.
pause
