# CyberQuest One-Command Startup Script for Windows PowerShell
# Usage: .\start.ps1

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "         CYBERQUEST — CTF PLATFORM LAUNCHER              " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Setup Python Virtual Environment
$VenvPath = Join-Path $ScriptDir "backend\venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

if (-not (Test-Path $VenvPath)) {
    Write-Host "[+] Creating Python virtual environment in backend/venv..." -ForegroundColor Cyan
    python -m venv $VenvPath
}

# 2. Install Backend Dependencies
Write-Host "[+] Checking and installing Python dependencies..." -ForegroundColor Cyan
& $PythonExe -m pip install -r backend\requirements.txt --quiet

# 3. Seed Database and Generate Challenge Files
Write-Host "[+] Seeding database and generating challenge resources..." -ForegroundColor Cyan
& $PythonExe backend\seed.py

# 4. Launch Main Backend Server (Port 5000)
Write-Host "[+] Starting Main CyberQuest Backend Server on http://localhost:5000..." -ForegroundColor Green
Start-Process -FilePath $PythonExe -ArgumentList "backend\app.py" -WorkingDirectory $ScriptDir -WindowStyle Hidden

# 5. Launch Challenge 5 Vulnerable App (Port 5005)
Write-Host "[+] Starting Challenge 5 (The Broken Application) on http://localhost:5005..." -ForegroundColor Green
Start-Process -FilePath $PythonExe -ArgumentList "challenges\05_multi_stage_web\app.py" -WorkingDirectory $ScriptDir -WindowStyle Hidden

# 6. Launch Frontend Dev Server (Port 3000 / Vite)
Write-Host "[+] Starting Frontend React Application..." -ForegroundColor Green
Set-Location (Join-Path $ScriptDir "frontend")

if (-not (Test-Path "node_modules")) {
    Write-Host "[+] Installing npm packages..." -ForegroundColor Cyan
    npm install
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host " CyberQuest is running!" -ForegroundColor Yellow
Write-Host " Main Platform:  http://localhost:3000" -ForegroundColor Cyan
Write-Host " Backend API:    http://localhost:5000" -ForegroundColor Cyan
Write-Host " Challenge 5:    http://localhost:5005" -ForegroundColor Cyan
Write-Host " Demo Credentials: admin / AdminPass123! or hacker1 / Hacker123!" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host ""

npm run dev
