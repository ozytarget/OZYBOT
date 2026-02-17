# Trading Bot - Scripts de Inicio

## 🚀 Inicio Rápido

### Windows

**Opción 1: Usar los scripts incluidos**

1. **Iniciar Backend:**

```cmd
backend\start.bat
```

1. **Iniciar Frontend:**

```cmd
cd frontend
npm run dev
```

**Opción 2: Iniciar todo en una terminal**

1. Abre PowerShell en la carpeta del proyecto
2. Ejecuta:

```powershell
# Backend (en una terminal)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; ..\.venv\Scripts\python.exe app.py"

# Frontend (en otra terminal)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
```

### Verificar que está funcionando

```powershell
# Verificar puertos activos
Get-NetTCPConnection -LocalPort 5000,3000 -State Listen
```

## 📱 URLs de Acceso

- **Frontend:** <http://localhost:3000> (o <http://localhost:3001> si 3000 está ocupado)
- **Backend API:** <http://localhost:5000>
- **Health Check:** <http://localhost:5000/health>

## 🔧 Detener los Servicios

Presiona `Ctrl + C` en cada terminal donde están corriendo los servicios.

## 📊 Estado Actual

Servicios activos:

- ✅ Backend corriendo en puerto 5000
- ✅ Frontend corriendo en puerto 3001

## 🎯 Próximos Pasos

1. Abre tu navegador en: **<http://localhost:3001>**
2. Registra una cuenta nueva
3. Configura el bot en Settings
4. Activa el bot desde el Dashboard
