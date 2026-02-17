# Guía de Configuración TradingView Webhook

## 🌐 EXPONER EL BOT A INTERNET CON NGROK

### Paso 1: Instalar ngrok

1. **Descargar ngrok:**
   - Ve a: <https://ngrok.com/download>
   - Descarga la versión para Windows
   - Descomprime el archivo en `C:\ngrok`

2. **Crear cuenta gratuita:**
   - Registrate en: <https://dashboard.ngrok.com/signup>
   - Copia tu token de autenticación

3. **Configurar ngrok:**

```powershell
cd C:\ngrok
.\ngrok.exe authtoken TU_TOKEN_AQUI
```

### Paso 2: Exponer el puerto 5000

En una nueva terminal PowerShell:

```powershell
cd C:\ngrok
.\ngrok.exe http 5000
```

Verás algo como:

```
Forwarding    https://abc123.ngrok.io -> http://localhost:5000
```

**⚠️ IMPORTANTE:** Copia la URL `https://abc123.ngrok.io` - esta es tu URL pública

---

## 📡 PASO 3: CONFIGURAR ALERTA EN TRADINGVIEW

### En TradingView

1. **Abre tu gráfico** con el indicador configurado

2. **Clic derecho en el indicador** → **"Add alert"** (o ícono de campana)

3. **Configurar la alerta:**

   **Condition:** Tu indicador → Condición que quieras (ej: "Buy Signal", "Sell Signal")

4. **En "Webhook URL":**

```
https://tu-url-ngrok.ngrok.io/webhook
```

   (Reemplaza con tu URL de ngrok)

1. **En "Message" (JSON):**

**Para señal de COMPRA:**

```json
{
  "symbol": "{{ticker}}",
  "action": "buy",
  "price": {{close}},
  "quantity": 0.1
}
```

**Para señal de VENTA:**

```json
{
  "symbol": "{{ticker}}",
  "action": "sell",
  "price": {{close}},
  "quantity": 0.1
}
```

1. **Configuración adicional:**
   - Nombre: "Bot Trading Alert"
   - Condition: Once per bar close (o según tu estrategia)
   - Expiration: No expira

2. **Haz clic en "Create"**

---

## ✅ VERIFICAR QUE FUNCIONA

### Prueba manual

En PowerShell, prueba enviar una alerta de prueba:

```powershell
$body = @{
    symbol = "BTCUSD"
    action = "buy"
    price = 50000
    quantity = 0.1
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://tu-url-ngrok.ngrok.io/webhook" -Method Post -Body $body -ContentType "application/json"
```

Si funciona, verás:

```json
{
  "status": "received",
  "message": "Webhook processed successfully"
}
```

---

## 🔄 FLUJO COMPLETO

1. ✅ Bot corriendo en puerto 5000
2. ✅ ngrok exponiendo puerto 5000 a Internet
3. ✅ TradingView envía webhook a ngrok
4. ✅ ngrok reenvía a tu bot local
5. ✅ Bot procesa la señal
6. ✅ Bot ejecuta la operación (si tienes broker conectado)

---

## 📊 MONITOREAR ALERTAS

En tu terminal del backend verás:

```
Webhook received: {'symbol': 'BTCUSD', 'action': 'buy', ...}
```

En tu Dashboard del bot verás las nuevas posiciones.

---

## 🚨 IMPORTANTE

- **ngrok gratis** genera URLs aleatorias que cambian cada vez que reinicias
- Si reinicias ngrok, debes **actualizar la URL en TradingView**
- **ngrok de pago** te da URLs fijas
- Para producción, usa un servidor con IP pública

---

## 🔐 SEGURIDAD (OPCIONAL)

Para agregar autenticación al webhook, edita `backend/routes/webhook.py`:

```python
WEBHOOK_SECRET = "tu-secreto-seguro-123"

# En la función tradingview_webhook:
if data.get('secret') != WEBHOOK_SECRET:
    return jsonify({'error': 'Invalid secret'}), 401
```

Y en TradingView, en el JSON del mensaje:

```json
{
  "secret": "tu-secreto-seguro-123",
  "symbol": "{{ticker}}",
  "action": "buy",
  "price": {{close}}
}
```
