
@echo off
REM Setup project
start "Setup  process" cmd /k "source .venv/bin/activate && python ./src/setup.py"

REM Keep the window open
pause