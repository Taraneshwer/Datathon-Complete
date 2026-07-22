<#
.SYNOPSIS
Builds the frontend and starts the backend.
#>

Write-Host "Building frontend..." -ForegroundColor Cyan
Set-Location -Path "frontend"
npm install
npm run dev
Set-Location -Path ".."

Write-Host "Starting backend..." -ForegroundColor Cyan
python -m uvicorn app.main:app --reload --port 8000
