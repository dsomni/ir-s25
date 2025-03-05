@echo off
REM Start FastAPI backend
start "FastAPI Backend" cmd /k ".venv\Scripts\activate && fastapi run"

REM Start Next.js frontend
start "Next.js Frontend" cmd /k "cd frontend && yarn build && yarn start"

REM Keep the window open
pause