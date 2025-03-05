#!/bin/bash

# Start FastAPI backend
source .venv/bin/activate && fastapi dev &

# Start Next.js frontend
cd ./frontend && yarn dev &

# Wait for both processes to finish
wait