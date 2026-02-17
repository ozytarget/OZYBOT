# 🚀 DEPLOYMENT GUIDE - GitHub + Railway

## ✅ PASO 1: SUBIR A GITHUB (COMPLETADO)

Tu repositorio: https://github.com/ozytarget/OZYBOT

---

## 📤 PASO 2: SUBIR EL CÓDIGO

Ejecuta estos comandos en PowerShell (en la carpeta copilot-bot):

```powershell
cd c:\Users\urbin\copilot-bot

# Inicializar git
git init

# Agregar todos los archivos
git add .

# Hacer el primer commit
git commit -m "Initial commit - Trading Bot"

# Conectar con tu repositorio
git remote add origin https://github.com/ozytarget/OZYBOT.git

# Subir el código
git branch -M main
git push -u origin main
```

Si te pide credenciales, usa tu Personal Access Token de GitHub.

---

## 🚂 PASO 3: DESPLEGAR EN RAILWAY

### 3.1 Crear cuenta en Railway

1. Ve a: **https://railway.app**
2. Haz clic en **"Start a New Project"**
3. Conecta con tu cuenta de GitHub
4. Da permisos a Railway para acceder a tus repositorios

### 3.2 Crear proyecto desde GitHub

1. Haz clic en **"Deploy from GitHub repo"**
2. Selecciona: **ozytarget/OZYBOT**
3. Railway detectará automáticamente que es un proyecto Python

### 3.3 Configurar Variables de Entorno

En Railway, ve a tu proyecto → **Variables** → Agrega:

```
SECRET_KEY=tu-clave-super-secreta-aqui-cambiar-123456
FLASK_ENV=production
PORT=5000
DATABASE_PATH=/app/trading.db
```

### 3.4 Esperar el Deploy

- Railway construirá y desplegará automáticamente
- Verás logs en tiempo real
- Cuando termine, obtendrás una URL pública

### 3.5 Obtener la URL

1. En Railway, haz clic en tu servicio
2. Ve a **Settings** → **Domains**
3. Haz clic en **"Generate Domain"**
4. Obtendrás algo como: `https://ozybot-production.up.railway.app`

---

## 🌐 PASO 4: CONFIGURAR FRONTEND PARA PRODUCCIÓN

Actualiza la URL del backend en el frontend:

**Archivo:** `frontend/src/api.js`

Cambia:
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

Por:
```javascript
const API_BASE_URL = 'https://tu-url-railway.up.railway.app';
```

Luego sube el cambio:
```powershell
git add .
git commit -m "Update API URL for production"
git push
```

Railway lo redesplegarajá automáticamente.

---

## 📡 PASO 5: CONFIGURAR TRADINGVIEW

Tu webhook URL será:
```
https://tu-url-railway.up.railway.app/webhook
```

En TradingView:
1. Crea tu alerta
2. Activa Webhook URL
3. Pon: `https://tu-url-railway.up.railway.app/webhook`
4. Message (JSON):
```json
{
  "symbol": "{{ticker}}",
  "action": "buy",
  "price": {{close}},
  "quantity": 0.1
}
```

---

## ✅ VERIFICAR QUE TODO FUNCIONA

1. **Health Check:** `https://tu-url-railway.up.railway.app/health`
2. **API Root:** `https://tu-url-railway.up.railway.app/`
3. **Frontend:** Abre la URL de Railway en tu navegador
4. **Webhook Test:** Usa curl o Postman para probar

```powershell
$body = @{
    symbol = "BTCUSD"
    action = "buy"
    price = 50000
    quantity = 0.1
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://tu-url-railway.up.railway.app/webhook" -Method Post -Body $body -ContentType "application/json"
```

---

## 🎯 VENTAJAS DE RAILWAY

✅ **Gratis** para empezar ($5 de crédito mensual)
✅ **HTTPS automático** (SSL incluido)
✅ **URL permanente** (no cambia como ngrok)
✅ **24/7 online** (no necesitas tu PC encendida)
✅ **Auto-deploy** (cada push a GitHub se despliega automáticamente)
✅ **Logs en tiempo real**
✅ **Base de datos persistente**

---

## 🔒 IMPORTANTE - SEGURIDAD

Después del deploy:

1. ✅ Cambia `SECRET_KEY` en las variables de entorno de Railway
2. ✅ Usa contraseñas seguras para tu cuenta
3. ✅ Nunca subas `.env` a GitHub (ya está en `.gitignore`)
4. ✅ Agrega autenticación al webhook si lo deseas

---

## 📊 MONITOREO

En Railway puedes ver:
- **Logs:** En tiempo real
- **Métricas:** CPU, RAM, Network
- **Deployments:** Historial de deployments
- **Variables:** Gestión de variables de entorno

---

## 🚨 TROUBLESHOOTING

**Si el deploy falla:**
1. Revisa los logs en Railway
2. Verifica que `requirements.txt` esté correcto
3. Asegúrate que `PORT` esté en las variables de entorno

**Si la base de datos se borra:**
- Railway usa almacenamiento efímero en el plan gratuito
- Para persistencia, considera Railway Postgres (plan de pago)
- O usa Railway Volumes

---

## 📱 PRÓXIMOS PASOS

1. ✅ Sube el código a GitHub
2. ✅ Despliega en Railway
3. ✅ Actualiza URL del frontend
4. ✅ Configura TradingView
5. ✅ ¡Empieza a tradear! 🚀
