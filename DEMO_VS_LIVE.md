# 🎯 DEMO MODE vs LIVE MODE

## ✅ TU STACK ES CORRECTO PARA TRADING REAL

**React/JavaScript es el estándar de la industria:**
- Robinhood: React
- Coinbase: React  
- Binance: React/TypeScript
- TradingView: JavaScript
- Interactive Brokers: React
- Webull: React

**NO NECESITAS CAMBIAR EL FRONTEND.** El problema no es el lenguaje, es la integración con brokers reales.

---

## 📊 MODO ACTUAL: DEMO (Simulado)

### ¿Qué hace DEMO mode?

```python
# backend/routes/webhook.py - Línea 126
def process_demo_signal(ticker, signal, price):
    """Process trading signal in DEMO mode (without real broker API)"""
    # Crea posiciones simuladas en la base de datos
    # NO ejecuta órdenes reales
    # NO usa dinero real
```

**Posiciones actuales:**
- AMZN @ $201.29 → **Simulada** (no existe en broker real)
- BTCUSD @ $67,722 → **Simulada** (no existe en broker real)

---

## 🚀 ACTIVAR LIVE MODE (Trading Real)

### Paso 1: Obtener API Keys de Broker Real

#### Opción A: Alpaca (Recomendado para empezar)
```bash
# 1. Regístrate en: https://alpaca.markets
# 2. Obtén API Keys (PAPER TRADING primero)
# 3. Agrega a backend/.env:

ALPACA_API_KEY=PK...
ALPACA_API_SECRET=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading (sin dinero real)
```

**Paper Trading:** Simula con datos reales pero sin arriesgar dinero real (ideal para testing)

#### Opción B: Binance (Para Crypto)
```bash
# 1. Regístrate en: https://www.binance.com
# 2. Crea API Key con permisos de trading
# 3. Agrega a backend/.env:

BINANCE_API_KEY=...
BINANCE_API_SECRET=...
```

#### Opción C: Interactive Brokers (Institucional)
```bash
# Requiere cuenta aprobada y software TWS/Gateway
IB_GATEWAY_HOST=localhost
IB_GATEWAY_PORT=4001
IB_ACCOUNT_ID=...
```

---

### Paso 2: Modificar webhook.py para usar broker real

**ANTES (DEMO):**
```python
# backend/routes/webhook.py - Línea 111
# Process trading signal in DEMO mode
process_demo_signal(ticker, signal, price)
```

**DESPUÉS (LIVE):**
```python
# backend/routes/webhook.py
from services.broker_integration import broker_service

# Process trading signal in LIVE mode
if demo_mode:
    process_demo_signal(ticker, signal, price)
else:
    # LIVE MODE - USA DINERO REAL ⚠️
    result = broker_service.place_order_real(
        symbol=ticker,
        side=signal.lower(),
        quantity=calculate_position_size(),
        order_type='market'
    )
    
    if result['success']:
        # Guardar posición real en base de datos
        save_live_position(result)
```

---

### Paso 3: Cambiar demo_mode a False en base de datos

```sql
-- SQLite: trading_bot.db
UPDATE bot_config SET demo_mode = 0 WHERE id = 1;
```

O desde el Dashboard:
```javascript
// frontend/src/pages/Settings.jsx
// Agregar toggle para activar/desactivar DEMO mode
```

---

## ⚠️ ADVERTENCIA: LIVE MODE USA DINERO REAL

### Antes de activar LIVE mode:

1. ✅ **Testea en Paper Trading** (Alpaca paper-api)
2. ✅ **Configura Stop Loss** en Settings
3. ✅ **Define tamaño de posición máximo** (ej: $100 por trade)
4. ✅ **Valida tu estrategia** con datos históricos
5. ✅ **Empieza con cantidades pequeñas**

### Ejemplo de configuración segura:

```python
# backend/config.py
MAX_POSITION_SIZE = 100  # Máximo $100 por trade
MAX_PORTFOLIO_RISK = 500  # Máximo $500 en todas las posiciones
STOP_LOSS_PERCENT = 2.0  # Stop Loss al -2%
```

---

## 🎯 ARQUITECTURA: DEMO vs LIVE

### DEMO Mode (Actual)
```
TradingView Webhook → Flask Backend → SQLite (simula posición)
                                   → Frontend muestra posición simulada
```

### LIVE Mode (Real)
```
TradingView Webhook → Flask Backend → Broker API (Alpaca/Binance)
                                   ↓
                                Orden ejecutada en mercado real
                                   ↓
                                SQLite (guarda confirmación)
                                   ↓
                                Frontend muestra posición real
```

---

## 📝 CHECKLIST: Pasar de DEMO a LIVE

- [ ] Obtener API Keys de broker (Alpaca Paper Trading recomendado)
- [ ] Agregar credenciales a `backend/.env`
- [ ] Implementar `broker_integration.py` (ya creado)
- [ ] Modificar `webhook.py` para llamar broker real
- [ ] Agregar toggle DEMO/LIVE en Settings frontend
- [ ] Testear en Paper Trading primero
- [ ] Configurar Stop Loss y límites de riesgo
- [ ] Validar con cantidades pequeñas
- [ ] Monitorear logs de ejecución real

---

## 💡 RESUMEN

| Aspecto | DEMO Mode | LIVE Mode |
|---------|-----------|-----------|
| **Frontend** | ✅ React (correcto) | ✅ React (mismo) |
| **Backend** | ✅ Python Flask | ✅ Python Flask |
| **Ejecución** | ❌ Simulada en BD | ✅ API Real del Broker |
| **Dinero** | ❌ Sin riesgo | ⚠️ Dinero real |
| **Datos** | ✅ Precios reales (yfinance) | ✅ Precios reales (broker) |

**Conclusión:** Tu stack tecnológico (React + Python) es **100% válido para trading real**. Solo necesitas:
1. API Keys de broker real
2. Integración con broker_service
3. Cambiar demo_mode a False

**NO necesitas cambiar de lenguaje.** React es el estándar de la industria para plataformas de trading.
