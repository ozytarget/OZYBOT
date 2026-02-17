# 🌐 DESPLEGAR FRONTEND EN VERCEL

## 📋 PASO A PASO

### 1. Actualizar URL del Backend

**Primero necesitas tu URL de Railway del backend.**

En el archivo `frontend/src/api.js`, actualiza la línea 3:

```javascript
// CAMBIA ESTO:
: 'https://ozybot-production.up.railway.app';

// POR TU URL DE RAILWAY:
: 'https://TU-URL-RAILWAY-AQUI.up.railway.app';
```

Guarda el cambio y haz commit:
```powershell
cd c:\Users\urbin\copilot-bot
git add .
git commit -m "Update backend URL for production"
git push
```

---

### 2. Ir a Vercel

1. **Ve a:** https://vercel.com
2. **Sign Up / Login** con tu cuenta de GitHub
3. Autoriza a Vercel

---

### 3. Importar Proyecto

1. Haz clic en **"Add New..."** → **"Project"**
2. Busca el repositorio: **`ozytarget/OZYBOT`**
3. Haz clic en **"Import"**

---

### 4. Configurar el Proyecto

En la pantalla de configuración:

**Framework Preset:** Vite
**Root Directory:** `frontend` ⚠️ MUY IMPORTANTE
**Build Command:** `npm run build`
**Output Directory:** `dist`

---

### 5. Variables de Entorno (Opcional)

Si necesitas alguna variable, agrégala aquí. Por ahora no es necesario.

---

### 6. Deploy

1. Haz clic en **"Deploy"**
2. Espera 1-2 minutos
3. Vercel te dará una URL como: `https://ozybot.vercel.app`

---

## ✅ RESULTADO

Tendrás:

✅ **Backend API:** `https://tu-url-railway.up.railway.app` (Railway)
✅ **Frontend Web:** `https://ozybot.vercel.app` (Vercel)

---

## 🎯 USAR LA APLICACIÓN

1. Abre tu URL de Vercel en el navegador
2. Verás la pantalla de Login/Register
3. Crea tu cuenta
4. Configura el bot en Settings
5. Activa el bot en Dashboard

---

## 📡 WEBHOOK PARA TRADINGVIEW

Tu webhook URL es la de Railway (backend):
```
https://tu-url-railway.up.railway.app/webhook
```

---

## 🔄 ACTUALIZACIONES FUTURAS

Cada vez que hagas cambios:

1. Haz commit y push a GitHub
2. Vercel y Railway se actualizarán automáticamente

---

## 🆘 SI ALGO FALLA

**Si el frontend no conecta con el backend:**
1. Verifica que actualizaste la URL en `frontend/src/api.js`
2. Asegúrate que el backend tenga CORS habilitado (ya lo tiene)
3. Revisa los logs en Vercel

**Si Vercel no encuentra los archivos:**
1. Asegúrate de poner `frontend` como Root Directory
2. Verifica que el Build Command sea `npm run build`
