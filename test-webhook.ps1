# Test Webhook Script
param(
    [string]$url = "http://localhost:5000/webhook"
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Probando Webhook" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL: $url" -ForegroundColor White
Write-Host ""

# Test data - Buy signal
$buySignal = @{
    symbol   = "BTCUSD"
    action   = "buy"
    price    = 50000.50
    quantity = 0.1
} | ConvertTo-Json

Write-Host "Enviando señal de COMPRA..." -ForegroundColor Yellow
Write-Host $buySignal -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Body $buySignal -ContentType "application/json"
    Write-Host "✅ RESPUESTA:" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json) -ForegroundColor White
}
catch {
    Write-Host "❌ ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifica que el backend esté corriendo en puerto 5000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
