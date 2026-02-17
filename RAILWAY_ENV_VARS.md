# Variables de Entorno para Railway

## 🔧 Variables que DEBES configurar en Railway

Ve a tu proyecto en Railway → Variables → Add Variable

### 1️⃣ SECRET_KEY (OBLIGATORIA)
```
SECRET_KEY=TuClaveSecretaSuperSegura123!@#
```

**¿Para qué?** 
- Encriptar tokens JWT
- Seguridad de sesiones

**Genera una aleatoria:**
```powershell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### 2️⃣ FLASK_ENV (RECOMENDADA)
```
FLASK_ENV=production
```

**¿Para qué?** 
- Desactivar modo debug
- Optimizar rendimiento

### 3️⃣ PORT (Automática - NO la configures)
Railway la configura automáticamente. **NO agregues esta variable.**

### 4️⃣ DATABASE_PATH (Opcional)
```
DATABASE_PATH=/app/trading.db
```

**¿Para qué?**
- Ubicación de la base de datos SQLite
- Por defecto usa `trading.db` en el directorio actual

## ✅ Configuración Completa en Railway

1. Abre https://railway.app
2. Ve a tu proyecto "OZYBOT"
3. Haz clic en el servicio (backend)
4. Pestaña **"Variables"**
5. Haz clic en **"+ New Variable"**
6. Agrega:

```
SECRET_KEY=GeneraUnaClaveAleatoriaSuperSegura32Caracteres
FLASK_ENV=production
```

## 🔐 Generar SECRET_KEY Segura

**Opción 1 - PowerShell:**
```powershell
-join ((65..90) + (97..122) + (48..57) + (33..47) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

**Opción 2 - Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Opción 3 - Online:**
Usa: https://randomkeygen.com/ (CodeIgniter Encryption Keys)

## 📋 Resumen

| Variable | ¿Necesaria? | Valor |
|----------|-------------|-------|
| SECRET_KEY | ✅ SÍ | Tu clave secreta aleatoria |
| FLASK_ENV | ⚠️ Recomendada | `production` |
| PORT | ❌ NO | Railway la pone automáticamente |
| DATABASE_PATH | ⚪ Opcional | `/app/trading.db` |

## 🚀 Después de Configurar

1. Railway redesplegarÁ automáticamente
2. Espera 1-2 minutos
3. Prueba: https://botz.up.railway.app/health

Si respondecon `{"status":"healthy"}` → ✅ Todo bien

## ⚠️ IMPORTANTE

**NO subas SECRET_KEY a GitHub**
- Ya está en `.gitignore` 
- Solo configúrala en Railway
- Usa una diferente en local (.env) y producción (Railway)

## 🔍 Ver Variables Actuales

Railway → Tu proyecto → Variables

Si ya está funcionando sin configurarlas, Railway usa los valores por defecto del código, pero **deberías configurar SECRET_KEY** para seguridad.
