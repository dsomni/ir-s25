@echo off
REM Start FastAPI backend
start "FastAPI Backend" cmd /k ".venv\Scripts\activate && fastapi dev"

REM Start Next.js frontend
start "Next.js Frontend" cmd /k "cd frontend && yarn dev"

REM Keep the window open
pause