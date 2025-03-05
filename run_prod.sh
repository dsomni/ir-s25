#!/bin/bash

# Start FastAPI backend
source .venv/bin/activate && fastapi run &

# Start Next.js frontend
cd ./frontend
yarn build
yarn start

# Wait for both processes to finish
wait