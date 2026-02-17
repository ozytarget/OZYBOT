# 🗺️ MAPA COMPLETO DE LA ARQUITECTURA

## 📂 ESTRUCTURA DE CARPETAS

```
copilot-bot/
│
├── 📁 backend/                      # API Python Flask (Puerto 5000)
│   ├── app.py                       # Entry point, inicia servicios
│   ├── config.py                    # Configuración (SECRET_KEY, JWT)
│   ├── database.py                  # Inicialización de SQLite
│   ├── auth_utils.py                # JWT authentication
│   ├── requirements.txt             # Dependencias Python
│   ├── runtime.txt                  # Python 3.11.0 (Railway)
│   ├── .env                         # Variables de entorno (secretos)
│   │
│   ├── 📁 routes/                   # Endpoints REST API
│   │   ├── auth.py                  # POST /auth/register, /auth/login
│   │   ├── dashboard.py             # GET /dashboard/stats, /positions, /analytics
│   │   ├── settings.py              # GET/POST /settings/bot-config
│   │   └── webhook.py               # POST /webhook/tradingview (recibe señales)
│   │
│   ├── 📁 services/                 # Lógica de negocio (Background Services)
│   │   ├── price_monitor.py         # Actualiza precios cada 5s (yfinance)
│   │   ├── websocket_service.py     # WebSocket Binance (real-time crypto)
│   │   ├── trading_engine.py        # Trailing Stop, Break-Even, Parciales
│   │   ├── analytics_service.py     # Win Rate, Drawdown, Equity Curve
│   │   ├── notification_service.py  # Telegram, Discord webhooks
│   │   └── broker_integration.py    # Alpaca/Binance API (LIVE mode)
│   │
│   └── 📁 migrations/               # Database migrations
│       ├── add_demo_mode.py         # Agrega campo demo_mode
│       ├── add_auto_close.py        # Agrega SL/TP automático
│       ├── add_risk_management.py   # Agrega trailing, break-even, parciales
│       └── repair_database.py       # Repara estructura si falta algo
│
├── 📁 frontend/                     # React 18 + Vite (Puerto 5173)
│   ├── index.html
│   ├── package.json                 # Dependencias Node.js
│   ├── vite.config.js               # Configuración Vite
│   ├── vercel.json                  # Deploy config para Vercel
│   │
│   └── 📁 src/
│       ├── main.jsx                 # Entry point React
│       ├── App.jsx                  # Router principal
│       ├── App.css                  # Estilos globales
│       ├── api.js                   # Cliente HTTP (fetch)
│       │
│       ├── 📁 pages/                # Vistas principales
│       │   ├── Login.jsx            # Página de login/registro
│       │   ├── Dashboard.jsx        # Dashboard básico (legacy)
│       │   ├── DashboardProfessional.jsx  # Dashboard con componentes profesionales
│       │   └── Settings.jsx         # Configuración del bot
│       │
│       └── 📁 components/           # Componentes reutilizables
│           ├── PriceTicker.jsx      # Precio en tiempo real (verde/rojo)
│           ├── PriceTicker.css
│           ├── ConnectionStatus.jsx # LED indicator (🟢🔴🟠)
│           ├── ConnectionStatus.css
│           ├── EquityCurve.jsx      # Sparkline 24h
│           └── EquityCurve.css
│
├── 📁 .vercel/                      # Metadata de Vercel
├── 📄 railway.json                  # Config Railway deployment
├── 📄 vercel.json                   # Config Vercel deployment
│
└── 📚 DOCUMENTACIÓN
    ├── README.md                    # Introducción
    ├── START.md                     # Guía de inicio rápido
    ├── DEMO_VS_LIVE.md              # DEMO vs LIVE mode
    ├── DEPLOYMENT.md                # Deploy Railway + Vercel
    ├── PROFESSIONAL_FEATURES.md     # Features profesionales
    ├── TRADINGVIEW_SETUP.md         # Configurar TradingView webhook
    └── ARCHITECTURE_MAP.md          # Este archivo
```

---

## 🔄 FLUJO DE DATOS COMPLETO

### **1. SEÑAL DESDE TRADINGVIEW**

```mermaid
┌─────────────────┐
│  TradingView    │
│   📊 Chart      │
│                 │
│  Strategy:      │
│  - RSI < 30     │
│  - MACD cross   │
│  → BUY Signal   │
└────────┬────────┘
         │ HTTP POST
         │ /webhook/tradingview
         ▼
```

**Payload JSON:**
```json
{
  "ticker": "AMZN",
  "signal": "BUY",
  "price": 201.29,
  "time": "2026-02-17T20:55:38Z"
}
```

---

### **2. BACKEND PROCESA SEÑAL**

```
┌─────────────────────────────────────────────────────────┐
│  🐍 FLASK BACKEND (Railway)                             │
│                                                          │
│  📥 routes/webhook.py                                   │
│      ├─ Valida JSON                                     │
│      ├─ Verifica bot_config (is_active=1)              │
│      └─ Decide: DEMO mode o LIVE mode?                 │
│                                                          │
│  ┌──────────────────┬──────────────────┐               │
│  │   DEMO MODE      │   LIVE MODE      │               │
│  │   (actual)       │   (futuro)       │               │
│  ├──────────────────┼──────────────────┤               │
│  │ • Simula posición│ • Llama Alpaca   │               │
│  │ • Guarda en DB   │ • Ejecuta orden  │               │
│  │ • Sin dinero real│ • Dinero real ⚠️ │               │
│  └──────────────────┴──────────────────┘               │
│             ▼                    ▼                      │
│  ┌─────────────────────────────────────┐               │
│  │  📊 SQLite Database                 │               │
│  │  - positions (id, symbol, pnl)      │               │
│  │  - trading_stats (win_rate, etc)    │               │
│  │  - bot_config (demo_mode, is_active)│               │
│  └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

---

### **3. SERVICIOS BACKGROUND (Siempre Activos)**

```
┌───────────────────────────────────────────────────────────┐
│  🔧 BACKGROUND SERVICES (Auto-start en app.py)            │
│                                                            │
│  🔄 price_monitor.py (Thread cada 5s)                     │
│     ├─ SELECT * FROM positions WHERE status='open'        │
│     ├─ Para cada posición:                                │
│     │   ├─ yfinance.Ticker(symbol).history()              │
│     │   ├─ Calcula PnL: (current_price - entry) * qty     │
│     │   └─ UPDATE positions SET current_price, pnl        │
│     └─ check_stop_loss_take_profit()                      │
│                                                            │
│  📡 websocket_service.py (Async Thread)                   │
│     ├─ Conecta a: wss://stream.binance.com:9443          │
│     ├─ Suscribe a: btcusdt@trade, ethusdt@trade          │
│     ├─ Recibe precio cada ~1 segundo                      │
│     └─ Actualiza: last_prices[ticker] = {price, color}    │
│                                                            │
│  ⚙️ trading_engine.py (Llamado por Dashboard)             │
│     ├─ calculate_trailing_stop() - Mueve SL si sube 1%   │
│     ├─ should_break_even() - Activa si profit > 1.5%     │
│     ├─ calculate_partial_closes() - TP1@2%, TP2@5%       │
│     └─ check_slippage() - Rechaza si > 0.1%              │
│                                                            │
│  📊 analytics_service.py (On-demand)                      │
│     ├─ calculate_win_rate()                               │
│     ├─ calculate_drawdown()                               │
│     └─ get_equity_curve() - Snapshots 24h                │
│                                                            │
│  🔔 notification_service.py (Opcional)                    │
│     ├─ notify_position_opened() → Telegram/Discord        │
│     ├─ notify_position_closed() → P&L report             │
│     └─ notify_break_even_activated()                      │
└───────────────────────────────────────────────────────────┘
```

---

### **4. FRONTEND CONSULTA DATOS**

```
┌─────────────────────────────────────────────────────────┐
│  ⚛️ REACT FRONTEND (Vercel)                             │
│                                                          │
│  📱 DashboardProfessional.jsx                           │
│      ├─ useEffect(() => { loadData() }, [])            │
│      │                                                   │
│      ├─ GET /dashboard/stats         → Total Trades    │
│      ├─ GET /dashboard/positions     → Open/Closed     │
│      ├─ GET /dashboard/analytics     → Win Rate        │
│      ├─ GET /dashboard/equity-curve  → Balance 24h     │
│      └─ GET /dashboard/realtime-prices → Precios live  │
│                                                          │
│  🔄 setInterval(() => loadData(), 5000)  # Refresh 5s   │
│                                                          │
│  🧩 COMPONENTES:                                         │
│      ├─ <PriceTicker ticker="AMZN" />                   │
│      │   └─ Llama /realtime-prices cada 2s             │
│      │   └─ Color: verde ↑, rojo ↓, gris =             │
│      │                                                   │
│      ├─ <ConnectionStatus />                            │
│      │   └─ Llama /connection-status cada 3s           │
│      │   └─ LED: 🟢 connected, 🔴 disconnected         │
│      │                                                   │
│      └─ <EquityCurve />                                │
│          └─ Llama /equity-curve cada 60s               │
│          └─ SVG sparkline con tendencia                │
└─────────────────────────────────────────────────────────┘
```

---

## 🗄️ BASE DE DATOS SQLite

### **Esquema de Tablas:**

```sql
📊 users
├─ id (PK)
├─ username
├─ email
├─ password_hash
└─ created_at

📈 positions
├─ id (PK)
├─ user_id (FK → users.id)
├─ symbol (AMZN, BTCUSD, etc)
├─ side (buy/sell)
├─ quantity
├─ entry_price
├─ current_price          ← Actualizado por price_monitor
├─ pnl                    ← Calculado: (current - entry) * qty
├─ status (open/closed)
├─ opened_at
├─ closed_at
├─ exit_price
│
├─── 🆕 RISK MANAGEMENT (add_risk_management.py)
├─ highest_price          ← Tracker para trailing stop
├─ trailing_stop          ← Precio dinámico de SL
├─ break_even_active      ← Boolean
├─ tp1_closed             ← Boolean (50% cerrado @2%)
├─ tp2_closed             ← Boolean (50% cerrado @5%)
├─ remaining_quantity     ← Qty después de parciales
├─ close_reason           ← "Trailing Stop", "TP1", etc
└─ alert_price            ← Precio de alerta

📊 trading_stats
├─ id (PK)
├─ user_id (FK)
├─ total_trades
├─ winning_trades
├─ losing_trades
├─ total_profit
│
├─── 🆕 ANALYTICS (add_risk_management.py)
├─ max_drawdown           ← Máxima pérdida desde ATH
├─ current_drawdown       ← Pérdida actual desde ATH
├─ avg_profit             ← Promedio de trades ganadores
├─ avg_loss               ← Promedio de trades perdedores
├─ largest_win            ← Mayor ganancia individual
├─ largest_loss           ← Mayor pérdida individual
├─ consecutive_wins       ← Racha ganadora actual
└─ consecutive_losses     ← Racha perdedora actual

⚙️ bot_config
├─ id (PK)
├─ user_id (FK)
├─ is_active              ← Bot ON/OFF
├─ demo_mode              ← 1=DEMO, 0=LIVE
├─ auto_close_enabled
├─ stop_loss_percent
└─ take_profit_percent

🔪 partial_closes
├─ id (PK)
├─ position_id (FK → positions.id)
├─ quantity               ← Cantidad cerrada
├─ price                  ← Precio de cierre
├─ reason                 ← "TP1", "TP2"
└─ closed_at

📝 trade_logs
├─ id (PK)
├─ position_id (FK)
├─ action                 ← "ENTRY", "PARTIAL", "EXIT"
├─ price
├─ quantity
├─ reason                 ← "Trailing Stop", "Manual"
├─ slippage               ← Diferencia vs precio objetivo
├─ duration_minutes       ← Tiempo en posición
└─ created_at

🔌 connection_status
├─ id (PK)
├─ source                 ← "Binance", "Alpaca"
├─ status                 ← "connected", "disconnected"
├─ last_update
└─ latency_ms

📈 equity_curve
├─ id (PK)
├─ user_id (FK)
├─ snapshot_time
├─ total_balance          ← Balance en ese momento
└─ realized_profit
```

### **Relaciones:**
```
users (1) ─────────── (N) positions
users (1) ─────────── (1) trading_stats
users (1) ─────────── (1) bot_config
positions (1) ──────── (N) partial_closes
positions (1) ──────── (N) trade_logs
users (1) ─────────── (N) equity_curve
```

---

## 🌊 API ENDPOINTS (REST)

### **🔐 Autenticación**

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Crear usuario nuevo |
| POST | `/auth/login` | No | Login → JWT token |

### **📊 Dashboard**

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/dashboard/stats` | ✅ | Total trades, win rate, profit |
| GET | `/dashboard/positions` | ✅ | Lista de posiciones (open/closed) |
| GET | `/dashboard/analytics` | ✅ | Win rate, drawdown, avg profit/loss |
| GET | `/dashboard/equity-curve` | ✅ | Snapshots de balance 24h |
| GET | `/dashboard/connection-status` | No | Estado WebSocket (LED) |
| GET | `/dashboard/realtime-prices` | No | Precios en tiempo real |
| GET | `/dashboard/partial-closes/:id` | ✅ | Cierres parciales de posición |
| GET | `/dashboard/trade-logs` | ✅ | Logs forenses de trades |
| POST | `/dashboard/close-position/:id` | ✅ | Cerrar posición manualmente |

### **⚙️ Settings**

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/settings/bot-config` | ✅ | Configuración actual del bot |
| POST | `/settings/bot-config` | ✅ | Actualizar configuración |

### **📥 Webhook**

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/webhook/tradingview` | No | Recibe señales de TradingView |

---

## 🚀 DEPLOYMENT ARCHITECTURE

### **Producción (Railway + Vercel):**

```
┌──────────────────────────────────────────────────────────────┐
│                     INTERNET                                  │
└────────────────────┬─────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌───────────────┐
│   FRONTEND    │         │   BACKEND     │
│   (Vercel)    │◄────────┤   (Railway)   │
│               │  CORS   │               │
│ React + Vite  │ Enabled │ Flask + SQLite│
│ Port: 443     │         │ Port: 5000    │
│               │         │               │
│ Domain:       │         │ Domain:       │
│ frontend-     │         │ copilot-bot-  │
│ woad-five-    │         │ production-   │
│ 99.vercel.app │         │ xxxx.railway  │
└───────────────┘         └───────────────┘
        │                         │
        │                         │
        │                   ┌─────┴─────────┐
        │                   │                │
        │                   ▼                ▼
        │          ┌─────────────┐   ┌──────────────┐
        │          │  SQLite DB  │   │ Background   │
        │          │ (persistent)│   │  Services    │
        │          └─────────────┘   └──────────────┘
        │                                    │
        │                                    │
        ▼                                    ▼
┌─────────────┐                    ┌─────────────────┐
│ TradingView │                    │ External APIs   │
│  Webhook    │                    │ - Binance WS    │
│  Alerts     │                    │ - Yahoo Finance │
└─────────────┘                    │ - Alpaca (LIVE) │
                                   └─────────────────┘
```

### **Local Development:**

```
┌──────────────────────────────────────────────┐
│  LOCALHOST                                    │
│                                               │
│  ┌────────────────┐      ┌────────────────┐ │
│  │   FRONTEND     │      │    BACKEND     │ │
│  │   Port: 5173   │◄─────┤   Port: 5000   │ │
│  │                │ CORS │                │ │
│  │   npm run dev  │      │ python app.py  │ │
│  └────────────────┘      └────────────────┘ │
│         │                        │           │
│         │                        ▼           │
│         │               ┌─────────────────┐  │
│         │               │ SQLite Database │  │
│         │               │ trading_bot.db  │  │
│         │               └─────────────────┘  │
│         │                                     │
│         ▼                                     │
│  http://localhost:5173                       │
└──────────────────────────────────────────────┘
```

---

## 🔑 VARIABLES DE ENTORNO

### **Backend (.env):**

```bash
# JWT Auth
SECRET_KEY=tu_secret_key_aqui
JWT_SECRET_KEY=tu_jwt_secret

# Notifications (Opcional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=

# Broker APIs (Para LIVE mode)
ALPACA_API_KEY=
ALPACA_API_SECRET=
ALPACA_BASE_URL=https://paper-api.alpaca.markets

BINANCE_API_KEY=
BINANCE_API_SECRET=
```

### **Frontend (vercel.json):**

```json
{
  "env": {
    "VITE_API_URL": "https://copilot-bot-production-xxxx.railway.app"
  }
}
```

---

## 📊 FLUJO DE DATOS DETALLADO

### **Escenario: Usuario abre Dashboard**

```
1. Usuario → https://frontend-woad-five-99.vercel.app/
   └─ React Router: <DashboardProfessional />

2. useEffect() ejecuta loadData()
   ├─ api.getStats() → GET /dashboard/stats
   ├─ api.getPositions() → GET /dashboard/positions
   ├─ api.getAnalytics() → GET /dashboard/analytics
   └─ api.getEquityCurve() → GET /dashboard/equity-curve

3. Backend (Flask) procesa:
   ├─ auth_utils.py verifica JWT token
   ├─ dashboard.py ejecuta queries SQL
   └─ Responde con JSON

4. Frontend actualiza state:
   ├─ setStats(data)
   ├─ setPositions(data)
   ├─ setAnalytics(data)
   └─ React re-renderiza UI

5. Componentes individuales:
   ├─ <PriceTicker /> → cada 2s llama /realtime-prices
   ├─ <ConnectionStatus /> → cada 3s llama /connection-status
   └─ <EquityCurve /> → cada 60s llama /equity-curve

6. setInterval() refresca todo el dashboard cada 5s
```

### **Escenario: TradingView envía señal BUY**

```
1. TradingView Strategy Alert trigger
   └─ Webhook: POST https://railway.app/webhook/tradingview
   └─ Body: {"ticker":"AMZN","signal":"BUY","price":201.29}

2. Backend (webhook.py) recibe:
   ├─ Valida JSON payload
   ├─ Busca bot_config WHERE is_active=1
   └─ Verifica demo_mode

3. DEMO MODE (actual):
   ├─ Calcula quantity = balance / price
   ├─ INSERT INTO positions (symbol, side, entry_price, status='open')
   ├─ UPDATE trading_stats SET total_trades++
   └─ Responde: {"success": true, "message": "Demo position created"}

4. OPCIONAL: notification_service
   ├─ notify_position_opened()
   └─ Envía a Telegram: "🟢 BUY AMZN @ $201.29"

5. price_monitor (background):
   ├─ Detecta nueva posición open
   ├─ Empieza a actualizar current_price cada 5s
   └─ Calcula PnL automáticamente

6. Frontend (refresh automático):
   ├─ GET /dashboard/positions detecta nueva posición
   └─ Aparece en tabla "Active Positions"
```

---

## 🧩 ARQUITECTURA DE COMPONENTES

### **Frontend Components Tree:**

```
App.jsx
├─ <BrowserRouter>
│  ├─ <Route path="/login">
│  │  └─ <Login />
│  │
│  ├─ <Route path="/dashboard">
│  │  └─ <DashboardProfessional />
│  │     ├─ <ConnectionStatus api={api} />
│  │     ├─ <EquityCurve api={api} token={token} />
│  │     └─ Para cada posición:
│  │        └─ <PriceTicker ticker={pos.symbol} />
│  │
│  └─ <Route path="/settings">
│     └─ <Settings />
```

### **Backend Services Initialization:**

```python
# app.py (líneas 40-55)

1. init_db()                        # Crea tablas
2. run_migration()                  # Ejecuta migrations
3. price_monitor.start()            # Thread background
4. realtime_price_service.start()   # Thread WebSocket
5. app.run()                        # Inicia Flask server
```

---

## 🔒 SEGURIDAD

```
┌──────────────────────────────────────┐
│  CAPAS DE SEGURIDAD                  │
│                                       │
│  1. JWT Token Authentication          │
│     ├─ Login genera token            │
│     ├─ Token expira en 24h           │
│     └─ @token_required decorator     │
│                                       │
│  2. Password Hashing (bcrypt)        │
│     └─ Nunca guarda plaintext        │
│                                       │
│  3. CORS Configuration                │
│     └─ Solo permite frontend URL     │
│                                       │
│  4. Environment Variables             │
│     └─ Secretos en .env (no git)     │
│                                       │
│  5. SQL Injection Protection          │
│     └─ Parameterized queries (?, ?)  │
└──────────────────────────────────────┘
```

---

## 🎯 PUNTOS CLAVE

### **Tecnologías Core:**
- **Backend:** Python 3.11, Flask 3.0, SQLite, WebSockets
- **Frontend:** React 18, Vite 5, React Router 6
- **Deployment:** Railway (backend), Vercel (frontend)
- **Real-Time:** Binance WebSocket, Yahoo Finance REST API

### **Servicios Background:**
1. **price_monitor.py:** Actualiza precios cada 5 segundos
2. **websocket_service.py:** Stream de Binance para cryptos
3. **trading_engine.py:** Trailing stops, break-even, parciales
4. **analytics_service.py:** Cálculos de métricas (on-demand)
5. **notification_service.py:** Telegram/Discord (opcional)

### **Estado Actual:**
- ✅ DEMO Mode activo (simulado, sin dinero real)
- ✅ Real-time prices funcionando
- ✅ Todas las features profesionales implementadas
- ⏳ LIVE Mode pendiente (requiere API keys de broker)

### **Próximos Pasos:**
1. Configurar Alpaca API para Paper Trading
2. Implementar broker_integration.py completo
3. Agregar toggle DEMO/LIVE en Settings
4. Testing con capital mínimo

---

## 📦 ARCHIVOS DE CONFIGURACIÓN

| Archivo | Propósito |
|---------|-----------|
| `backend/requirements.txt` | Python dependencies |
| `backend/runtime.txt` | Python version (Railway) |
| `backend/.env` | Variables de entorno (local) |
| `frontend/package.json` | Node.js dependencies |
| `frontend/vercel.json` | Deploy config Vercel |
| `railway.json` | Deploy config Railway |
| `vercel.json` | Vercel project settings |

---

## 🔍 DEBUGGING & LOGS

### **Backend Logs (Railway):**
```bash
railway logs
# Ver:
# - "🔄 Actualizando X posiciones..."
# - "✅ BTCUSD: $67722 -> $67800"
# - "🔌 Conectado a Binance WebSocket"
```

### **Frontend Dev Console:**
```javascript
// Ver network requests:
// - GET /dashboard/stats → 200 OK
// - GET /realtime-prices → {"prices": {...}}
```

### **Database Inspection:**
```bash
cd backend
sqlite3 trading_bot.db
> SELECT * FROM positions WHERE status='open';
> SELECT * FROM trading_stats;
> .quit
```

---

## 🎓 LEARNING RESOURCES

Para entender mejor cada componente:

- **Flask:** https://flask.palletsprojects.com/
- **React:** https://react.dev/
- **WebSockets:** https://websockets.readthedocs.io/
- **TradingView Webhooks:** https://www.tradingview.com/support/solutions/43000529348
- **Alpaca API:** https://alpaca.markets/docs/

---

**Última actualización:** Febrero 17, 2026  
**Versión:** 2.0 (Professional Features Complete)
