#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# AppSail Serverless Startup Script for Project Rainfall
# 100% Zoho Catalyst-Native Architecture
# ─────────────────────────────────────────────────────────────────────────────
echo "Starting Project Rainfall 100% Catalyst-Native FastAPI server..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${X_ZOHO_CATALYST_LISTEN_PORT:-8000} --workers 1
