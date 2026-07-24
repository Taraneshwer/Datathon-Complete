#!/bin/bash

# Ensure AI packages are installed in the background to prevent server startup timeout.
# AppSail has already installed requirements.txt during the build phase.
# This strictly enforces that requirements.txt is installed BEFORE requirements-ai.txt.
echo "Installing AI dependencies in the background..."
nohup pip install --no-cache-dir -r requirements-ai.txt > ai_install.log 2>&1 &

echo "Starting FastAPI server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $X_ZOHO_CATALYST_LISTEN_PORT
