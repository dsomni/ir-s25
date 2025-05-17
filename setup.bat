
@echo off
REM Setup project
start "Setup  process" cmd /k ".venv\Scripts\activate && python ./src/setup.py"

REM Keep the window open
pause