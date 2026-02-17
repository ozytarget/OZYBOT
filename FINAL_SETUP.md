# 🚀 OZYBOT - CONFIGURACIÓN FINAL

## ✅ BACKEND DESPLEGADO

**URL Backend:** <https://botz.up.railway.app/>

**Endpoints disponibles:**

- Health: <https://botz.up.railway.app/health>
- API Info: <https://botz.up.railway.app/>
- Auth: <https://botz.up.railway.app/auth/>...
- Dashboard: <https://botz.up.railway.app/dashboard/>...
- Settings: <https://botz.up.railway.app/settings/>...
- Webhook: <https://botz.up.railway.app/webhook>

---

## 🌐 DESPLEGAR FRONTEND EN VERCEL (5 minutos)

### PASO 1: Ve a Vercel

👉 **<https://vercel.com>**

### PASO 2: Login con GitHub

- Haz clic en **"Sign Up"** o **"Login"**
- Selecciona **"Continue with GitHub"**
- Autoriza a Vercel para acceder a tus repositorios

### PASO 3: Importar Proyecto

1. Haz clic en **"Add New..."** → **"Project"**
2. Busca el repositorio: **`ozytarget/OZYBOT`**
3. Haz clic en **"Import"**

### PASO 4: Configurar el Deploy

⚠️ **MUY IMPORTANTE - Usa esta configuración exacta:**

```
Framework Preset: Vite
Root Directory: frontend  ← ¡Click en Edit y escribe "frontend"!
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

**Captura de ejemplo:**

```
┌──────────────────────────────────────┐
│ Configure Project                    │
├──────────────────────────────────────┤
│ Framework Preset:    [Vite       ▼] │
│ Root Directory:      [frontend     ] │ ← ¡IMPORTANTE!
│ Build Command:       npm run build   │
│ Output Directory:    dist            │
│ Install Command:     npm install     │
└──────────────────────────────────────┘
```

### PASO 5: Variables de Entorno (Opcional)

En **"Environment Variables"** → Agregar:

```
Name:  VITE_API_URL
Value: https://botz.up.railway.app
```

(Ya está configurado por defecto, pero si quieres puedes agregarlo)

### PASO 6: Deploy

1. Haz clic en **"Deploy"**
2. Vercel construirá tu proyecto (1-2 minutos)
3. Verás logs en pantalla
4. Cuando termine, te mostrará: **"Congratulations!"**

### PASO 7: Obtener tu URL

Vercel te dará una URL como:

```
https://ozybot.vercel.app
```

o

```
https://ozybot-ozytarget.vercel.app
```

---

## ✅ VERIFICAR QUE TODO FUNCIONA

### 1. Backend (Railway)

```
https://botz.up.railway.app/health
```

Deberías ver: `{"status":"healthy"}`

### 2. Frontend (Vercel)

Abre tu URL de Vercel en el navegador:

```
https://tu-app.vercel.app
```

Deberías ver:

- ✅ Pantalla de Login/Register
- ✅ Formulario funcional
- ✅ Sin errores en consola

---

## 🎯 USAR LA APLICACIÓN

### 1. Registrarte

1. Abre tu URL de Vercel
2. Haz clic en **"Register"**
3. Ingresa:
   - Email: `trader@ozybot.com`
   - Password: `trading123`
4. Haz clic en **"Register"**

### 2. Configurar el Bot

1. Ve a **"Settings"** (menú superior)
2. Configura:
   - Risk Level: **Medium**
   - Max Position Size: **$1000**
   - Stop Loss: **2%**
   - Take Profit: **5%**
3. Haz clic en **"Save Configuration"**

### 3. Configurar Broker (Opcional)

1. En Settings, sección "Broker Settings"
2. Ingresa tu broker y API keys
3. **"Save Broker Settings"**

### 4. Activar el Bot

1. Ve a **"Dashboard"**
2. Haz clic en **"Start Bot"** (botón verde)
3. El bot estará activo ✅

---

## 📡 CONFIGURAR TRADINGVIEW

Ahora puedes conectar tu indicador:

### URL del Webhook

```
https://botz.up.railway.app/webhook
```

### Configurar Alerta

1. **En TradingView:**
   - Abre tu gráfico con el indicador
   - Clic en el ícono de alerta 🔔

2. **Configuración:**
   - Condition: Tu indicador → señal que quieres
   - ✅ **Webhook URL:** `https://botz.up.railway.app/webhook`

3. **Message (JSON):**

**Para COMPRA:**

```json
{
  "symbol": "{{ticker}}",
  "action": "buy",
  "price": {{close}},
  "quantity": 0.1
}
```

**Para VENTA:**

```json
{
  "symbol": "{{ticker}}",
  "action": "sell",
  "price": {{close}},
  "quantity": 0.1
}
```

1. **Create Alert**

---

## ✅ RESULTADO FINAL

Tu sistema completo:

| Componente | URL | Estado |
|------------|-----|--------|
| **Backend API** | <https://botz.up.railway.app> | ✅ Online |
| **Frontend Web** | <https://tu-app.vercel.app> | 🔄 Por desplegar |
| **GitHub** | <https://github.com/ozytarget/OZYBOT> | ✅ Actualizado |

---

## 🧪 PROBAR WEBHOOK

Puedes probar el webhook manualmente:

**En PowerShell:**

```powershell
$body = @{
    symbol = "BTCUSD"
    action = "buy"
    price = 50000
    quantity = 0.1
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://botz.up.railway.app/webhook" -Method Post -Body $body -ContentType "application/json"
```

Deberías ver:

```json
{
  "status": "received",
  "message": "Webhook processed successfully"
}
```

---

## 🎉 VENTAJAS DE TU SETUP

✅ **24/7 Online** - No necesitas tu PC encendida
✅ **URLs Permanentes** - No cambian
✅ **HTTPS Seguro** - SSL incluido
✅ **Auto-Deploy** - Cada push se despliega automáticamente
✅ **Gratis** - Railway $5/mes + Vercel gratis
✅ **Escalable** - Puedes agregar más usuarios

---

## 🔒 SEGURIDAD

Tu bot ya tiene:
✅ JWT Authentication
✅ Password hashing con bcrypt
✅ CORS configurado
✅ HTTPS en ambos servicios

**Recomendaciones adicionales:**

- Cambia el `SECRET_KEY` en Railway (ya lo hiciste)
- Usa contraseñas fuertes
- Agrega webhook secret para TradingView

---

## 📱 PRÓXIMOS PASOS

1. ✅ Desplegar frontend en Vercel (sigue los pasos de arriba)
2. ✅ Crear tu cuenta en la app
3. ✅ Configurar el bot
4. ✅ Conectar TradingView
5. ✅ ¡Empezar a tradear! 🚀

---

## 🆘 SOPORTE

**Si algo falla en Vercel:**

- Verifica que pusiste `frontend` como Root Directory
- Asegúrate que el Framework sea Vite
- Revisa los logs de build en Vercel

**Si el frontend no conecta con el backend:**

- Abre la consola del navegador (F12)
- Verifica que las llamadas vayan a `https://botz.up.railway.app`
- Revisa que CORS esté habilitado en Railway

---

## 📚 DOCUMENTACIÓN

- [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md) - Guía completa de Vercel
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment general
- [TRADINGVIEW_SETUP.md](./TRADINGVIEW_SETUP.md) - Configuración TradingView
- [README.md](./README.md) - Documentación principal

---

**¡Tu bot está listo! 🚀 Solo falta desplegarlo en Vercel!**
