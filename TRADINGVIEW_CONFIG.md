# Configuración de Webhooks en TradingView

## ✅ Webhook está funcionando

Tu webhook en Railway **está funcionando correctamente**:
- URL: `https://botz.up.railway.app/webhook`
- Estado: ✅ Activo y recibiendo datos

## 📋 Configuración en TradingView

### Paso 1: Crear Alerta

1. Abre TradingView
2. Haz clic derecho en el gráfico
3. Selecciona "Add Alert" (Añadir Alerta)

### Paso 2: Configurar Webhook

En la ventana de alerta:

#### Tab "Settings" (Configuración)
- Configura tu condición de alerta (precio, indicador, etc.)

#### Tab "Notifications" (Notificaciones)

**IMPORTANTE:** Debes marcar estas opciones:

✅ **Webhook URL** (obligatorio)
```
https://botz.up.railway.app/webhook
```

**VERIFICA:**
- ✅ Usa HTTPS (no HTTP)
- ✅ Sin espacios al inicio o final
- ✅ Sin barra final (/)

#### Tab "Message" (Mensaje)

Aquí defines qué datos enviar. Ejemplos:

**Formato Simple:**
```json
{
  "ticker": "{{ticker}}",
  "price": "{{close}}",
  "action": "buy"
}
```

**Formato con tu mensaje:**
```json
{
  "ticker": "{{ticker}}",
  "close": "{{close}}",
  "message": "ALERTA: {{ticker}} en {{close}}"
}
```

**Formato Completo:**
```json
{
  "symbol": "{{ticker}}",
  "action": "buy",
  "price": {{close}},
  "time": "{{time}}",
  "exchange": "{{exchange}}"
}
```

### Paso 3: Guardar y Probar

1. Haz clic en **"Create"** (Crear)
2. La alerta se creará
3. Cuando se dispare, TradingView enviará el webhook

## 🔍 Verificar que Funciona

### Opción 1: Ver en Dashboard
1. Abre: https://frontend-woad-five-99.vercel.app
2. Inicia sesión
3. Ve a Dashboard
4. Las alertas recibidas aparecerán en tiempo real

### Opción 2: Ver Logs en Railway
1. Abre Railway.app
2. Ve a tu proyecto "OZYBOT"
3. Haz clic en "View Logs"
4. Verás: `✅ Webhook #X received and saved: {...}`

## ❌ Problemas Comunes

### No llegan las alertas

**Revisa:**

1. **URL correcta:** 
   - ✅ `https://botz.up.railway.app/webhook`
   - ❌ `http://botz.up.railway.app/webhook` (sin HTTPS)
   - ❌ `https://botz.up.railway.app/webhook/` (con barra final)

2. **Checkbox marcado:**
   - ✅ "Webhook URL" debe estar marcado en Notifications

3. **Mensaje válido:**
   - ✅ JSON válido (con comillas dobles)
   - ❌ JSON inválido (comillas simples o sin cerrar)

4. **Alerta disparada:**
   - La alerta debe cumplir su condición para enviarse
   - Revisa el historial de alertas en TradingView

### Error de conexión

Si TradingView muestra error:
- Verifica que Railway esté online: https://botz.up.railway.app/health
- Debe responder: `{"status":"healthy"}`

## 📱 Ejemplo Completo

**Alerta de Precio:**
- Condición: BTCUSD > 50000
- Webhook URL: `https://botz.up.railway.app/webhook`
- Mensaje:
```json
{
  "symbol": "BTCUSD",
  "action": "buy",
  "price": {{close}},
  "alert": "Price above 50k"
}
```

Cuando BTC supere 50k:
1. TradingView dispara alerta
2. Envía POST a tu webhook
3. Railway guarda en base de datos
4. Aparece en tu dashboard

## 🎯 Prueba Manual

Puedes probar el webhook manualmente desde PowerShell:

```powershell
Invoke-RestMethod -Uri "https://botz.up.railway.app/webhook" -Method Post -Body '{"test":"manual","ticker":"BTCUSD"}' -ContentType "application/json"
```

Debe responder:
```json
{
  "status": "received",
  "message": "Webhook processed successfully",
  "data": {...}
}
```
