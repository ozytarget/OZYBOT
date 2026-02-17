# 🎯 RESUMEN VISUAL DE LA ARQUITECTURA

## 📱 ARQUITECTURA EN 1 IMAGEN

```
┌────────────────────────────────────────────────────────────────────────┐
│                          TRADING BOT SYSTEM                             │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│ TradingView │         │   FLASK BACKEND  │         │  REACT FRONTEND │
│   Charts    │──POST──▶│   (Railway)      │◀──GET──│    (Vercel)     │
│   Webhook   │ JSON    │   Port: 5000     │  JSON  │   Port: 443     │
└─────────────┘         └────────┬─────────┘         └─────────────────┘
                                 │
                        ┌────────┴────────┐
                        │                 │
                        ▼                 ▼
              ┌──────────────┐   ┌────────────────┐
              │   SQLite DB  │   │   BACKGROUND   │
              │              │   │    SERVICES    │
              │ • positions  │   │ • price_mon    │
              │ • stats      │   │ • websocket    │
              │ • config     │   │ • trading_eng  │
              └──────────────┘   │ • analytics    │
                                 │ • notifs       │
                                 └─────┬──────────┘
                                       │
                              ┌────────┴────────┐
                              ▼                 ▼
                       ┌──────────┐     ┌──────────────┐
                       │ Binance  │     │    Yahoo     │
                       │ WebSocket│     │   Finance    │
                       │ (Crypto) │     │   (Stocks)   │
                       └──────────┘     └──────────────┘
```

---

## 🔄 FLUJO DE UNA SEÑAL (3 PASOS)

```
PASO 1: TRADINGVIEW ENVÍA SEÑAL
┌─────────────────────────────────────┐
│ Strategy Alert Trigger              │
│ {"ticker":"AMZN","signal":"BUY"}    │
└─────────────┬───────────────────────┘
              │ POST /webhook/tradingview
              ▼
┌─────────────────────────────────────┐
│ PASO 2: BACKEND PROCESA             │
│ • Valida JSON                       │
│ • Verifica bot_config (is_active=1) │
│ • DEMO: Inserta en DB (simulado)    │
│ • LIVE: Llama Alpaca API (real) ⚠️  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ PASO 3: BACKGROUND SERVICES         │
│ • price_monitor: Actualiza precio   │
│ • trading_engine: Chequea trailing  │
│ • analytics: Calcula métricas       │
└─────────────────────────────────────┘
```

---

## 📊 ESTRUCTURA DE CARPETAS (SIMPLIFICADA)

```
copilot-bot/
│
├── backend/                    # Python Flask API
│   ├── app.py                  # ⭐ Entry point
│   ├── database.py             # SQLite setup
│   ├── routes/                 # API endpoints
│   │   ├── webhook.py          # Recibe TradingView
│   │   ├── dashboard.py        # Stats & positions
│   │   └── settings.py         # Bot config
│   └── services/               # Background logic
│       ├── price_monitor.py    # Actualiza precios
│       ├── websocket_service.py# Binance stream
│       ├── trading_engine.py   # Trailing stops
│       └── analytics_service.py# Win rate, etc
│
├── frontend/                   # React 18
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── DashboardProfessional.jsx  # ⭐ Main
│       │   └── Settings.jsx
│       └── components/
│           ├── PriceTicker.jsx      # Precio real-time
│           ├── ConnectionStatus.jsx # LED indicator
│           └── EquityCurve.jsx      # 24h chart
│
└── DOCS/
    ├── ARCHITECTURE_MAP.md     # ⭐ Mapa completo
    ├── DEMO_VS_LIVE.md         # DEMO vs LIVE mode
    └── START.md                # Quick start
```

---

## 🗄️ BASE DE DATOS (5 TABLAS PRINCIPALES)

```sql
users
└─ id, username, password_hash

positions ⭐ (La más importante)
├─ symbol (AMZN, BTCUSD)
├─ side (buy/sell)
├─ entry_price, current_price
├─ pnl (calculado automáticamente)
├─ status (open/closed)
└─ Risk Management:
   ├─ trailing_stop
   ├─ break_even_active
   ├─ tp1_closed, tp2_closed
   └─ remaining_quantity

trading_stats
├─ total_trades
├─ winning_trades, losing_trades
├─ max_drawdown, avg_profit
└─ consecutive_wins

bot_config
├─ is_active (ON/OFF)
├─ demo_mode (1=DEMO, 0=LIVE)
└─ stop_loss_percent

equity_curve
└─ Snapshots de balance 24h
```

---

## 🚀 API ENDPOINTS (TOP 10)

| # | Método | Endpoint | Qué hace |
|---|--------|----------|----------|
| 1 | POST | `/auth/login` | Login → JWT token |
| 2 | POST | `/webhook/tradingview` | **Recibe señales** |
| 3 | GET | `/dashboard/stats` | Total trades, win rate |
| 4 | GET | `/dashboard/positions` | Lista posiciones |
| 5 | GET | `/dashboard/analytics` | Win rate, drawdown |
| 6 | GET | `/dashboard/realtime-prices` | **Precios live** |
| 7 | GET | `/dashboard/equity-curve` | Balance 24h |
| 8 | GET | `/dashboard/connection-status` | LED indicator |
| 9 | POST | `/dashboard/close-position/:id` | Cierra posición |
| 10 | POST | `/settings/bot-config` | Config bot |

---

## ⚙️ SERVICIOS BACKGROUND (Siempre corriendo)

```
┌─────────────────────────────────────────────────────────┐
│  price_monitor.py          (Thread cada 5 segundos)     │
│  ✓ Actualiza current_price de todas las posiciones     │
│  ✓ Calcula PnL automáticamente                         │
│  ✓ Chequea Stop Loss / Take Profit                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  websocket_service.py      (Async Thread)               │
│  ✓ Conecta a Binance WebSocket                         │
│  ✓ Stream de precios crypto en ~1 segundo              │
│  ✓ Actualiza last_prices[ticker]                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  trading_engine.py         (On-demand)                  │
│  ✓ Trailing Stop: Mueve SL si sube 1%                  │
│  ✓ Break-Even: Activa si profit > 1.5%                 │
│  ✓ Parciales: TP1@2%, TP2@5%                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  analytics_service.py      (On-demand)                  │
│  ✓ Win Rate, Drawdown, Consecutive wins                │
│  ✓ Average Profit/Loss                                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  notification_service.py   (Opcional)                   │
│  ✓ Telegram/Discord webhooks                           │
│  ✓ Notifica al abrir/cerrar posiciones                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 COMANDOS IMPORTANTES

### **Backend (local):**
```bash
cd backend
python app.py
# Server running on http://localhost:5000
```

### **Frontend (local):**
```bash
cd frontend
npm run dev
# Server running on http://localhost:5173
```

### **Deploy:**
```bash
git add .
git commit -m "Tu mensaje"
git push origin main
# Railway auto-deploys backend
# Vercel auto-deploys frontend
```

### **Database:**
```bash
cd backend
sqlite3 trading_bot.db
> SELECT * FROM positions WHERE status='open';
```

---

## 📦 DEPENDENCIAS CLAVE

### **Backend:**
```
Flask 3.0.0          # Web framework
Flask-CORS 4.0.0     # Permite requests desde frontend
PyJWT 2.8.0          # JWT tokens
bcrypt 4.1.2         # Password hashing
yfinance 0.2.36      # Precios de stocks
websockets 12.0      # Binance real-time
requests 2.31.0      # HTTP client
```

### **Frontend:**
```
react 18.2.0         # UI library
react-dom 18.2.0     # React DOM
react-router-dom 6   # Routing
vite 5.0.8           # Build tool
```

---

## 🎯 DEMO vs LIVE MODE

| Aspecto | DEMO (Actual) | LIVE (Futuro) |
|---------|---------------|---------------|
| **Ejecución** | Simulada (SQLite) | Real (Alpaca/Binance API) |
| **Dinero** | Fake (sin riesgo) | Real (⚠️ riesgo) |
| **Precios** | Reales (yfinance) | Reales (broker) |
| **Posiciones** | Solo en DB | En broker + DB |
| **Configurar** | demo_mode=1 | demo_mode=0 + API Keys |

**Para pasar a LIVE:** Lee [DEMO_VS_LIVE.md](DEMO_VS_LIVE.md)

---

## 🔒 SEGURIDAD

1. **JWT Authentication:** Protege endpoints sensibles
2. **bcrypt:** Hash de passwords
3. **CORS:** Solo permite frontend autorizado
4. **Environment Variables:** Secretos en .env (no git)
5. **SQL Injection Protection:** Queries parametrizadas

---

## 🎓 DOCUMENTACIÓN COMPLETA

| Archivo | Descripción |
|---------|-------------|
| [ARCHITECTURE_MAP.md](ARCHITECTURE_MAP.md) | 🗺️ Mapa completo detallado |
| [DEMO_VS_LIVE.md](DEMO_VS_LIVE.md) | Pasar de DEMO a LIVE |
| [START.md](START.md) | Quick start guide |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deploy Railway + Vercel |
| [PROFESSIONAL_FEATURES.md](PROFESSIONAL_FEATURES.md) | Features implementados |
| [TRADINGVIEW_SETUP.md](TRADINGVIEW_SETUP.md) | Configurar webhook |

---

## ⚡ QUICK REFERENCE

### **URLs:**
- **Frontend:** https://frontend-woad-five-99.vercel.app
- **Backend:** https://copilot-bot-production-xxxx.railway.app
- **GitHub:** https://github.com/ozytarget/OZYBOT

### **Estado Actual:**
- ✅ DEMO Mode activo
- ✅ Real-time prices funcionando
- ✅ Todas las features profesionales OK
- ⏳ LIVE Mode pendiente (API keys)

### **Next Steps:**
1. Obtener API Keys de Alpaca (paper trading)
2. Agregar a Railway environment variables
3. Cambiar demo_mode a 0
4. Test con capital pequeño

---

**🎉 Todo está funcionando correctamente en DEMO mode.**  
**Lee [ARCHITECTURE_MAP.md](ARCHITECTURE_MAP.md) para detalles completos.**
