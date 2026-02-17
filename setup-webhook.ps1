# Setup TradingView Webhook - Script Automático
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  TradingView Webhook Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if ngrok exists
$ngrokPath = "C:\ngrok\ngrok.exe"
if (Test-Path $ngrokPath) {
    Write-Host "✅ ngrok encontrado en $ngrokPath" -ForegroundColor Green
} else {
    Write-Host "❌ ngrok NO encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "INSTALAR NGROK:" -ForegroundColor Yellow
    Write-Host "1. Ve a: https://ngrok.com/download" -ForegroundColor White
    Write-Host "2. Descarga ngrok para Windows" -ForegroundColor White
    Write-Host "3. Extrae el archivo a C:\ngrok\" -ForegroundColor White
    Write-Host "4. Registrate en: https://dashboard.ngrok.com/signup" -ForegroundColor White
    Write-Host "5. Copia tu authtoken" -ForegroundColor White
    Write-Host "6. Ejecuta: C:\ngrok\ngrok.exe authtoken TU_TOKEN" -ForegroundColor White
    Write-Host ""
    Write-Host "Presiona Enter cuando hayas instalado ngrok..." -ForegroundColor Yellow
    Read-Host
}

# Check if ngrok is configured
if (Test-Path $ngrokPath) {
    Write-Host ""
    Write-Host "Iniciando ngrok en puerto 5000..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Red
    Write-Host "   1. Copia la URL que aparece (https://xxxxx.ngrok.io)" -ForegroundColor White
    Write-Host "   2. Usa esa URL en TradingView: https://xxxxx.ngrok.io/webhook" -ForegroundColor White
    Write-Host ""
    Write-Host "Presiona Ctrl+C para detener ngrok" -ForegroundColor Gray
    Write-Host ""
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\ngrok; .\ngrok.exe http 5000"
    
    Start-Sleep -Seconds 5
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "  SIGUIENTE PASO:" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "1. Copia la URL de ngrok (https://xxxxx.ngrok.io)" -ForegroundColor White
    Write-Host "2. Ve a TradingView" -ForegroundColor White
    Write-Host "3. Crea una alerta en tu indicador" -ForegroundColor White
    Write-Host "4. En Webhook URL pon: https://xxxxx.ngrok.io/webhook" -ForegroundColor White
    Write-Host "5. En Message pon el JSON (ver TRADINGVIEW_SETUP.md)" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "❌ No se puede continuar sin ngrok" -ForegroundColor Red
}
