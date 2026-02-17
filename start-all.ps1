# Trading Bot Startup Script
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Trading Bot - Iniciando..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Backend
Write-Host "[1/2] Iniciando Backend (Puerto 5000)..." -ForegroundColor Yellow
$backendPath = Join-Path $scriptDir "backend"
$pythonPath = Join-Path $scriptDir ".venv\Scripts\python.exe"
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; & '$pythonPath' app.py" -PassThru
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "[2/2] Iniciando Frontend (Puerto 3000)..." -ForegroundColor Yellow
$frontendPath = Join-Path $scriptDir "frontend"
$frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -PassThru
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "  ✅ Servicios Iniciados" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Presiona Ctrl+C en cada terminal para detener los servicios" -ForegroundColor Gray
Write-Host ""

# Wait a bit and try to open browser
Start-Sleep -Seconds 5
Write-Host "Abriendo navegador..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"
