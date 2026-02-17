# 🚀 Professional Trading Bot Platform

Full-stack quantitative trading platform with advanced risk management, real-time data, and professional analytics.

## 🎯 Professional Features

### 1. Real-Time Price Monitoring
- **WebSocket Integration**: Live price feeds from Binance
- **Color-Coded Ticker**: Prices flash green (up), red (down), gray (no change)
- **Sub-second Updates**: Real-time price tracking every second
- **Connection Status LED**: Visual indicator showing exchange connectivity

### 2. Advanced Risk Management
- **Trailing Stop Loss**: Dynamically follows price movements (1% trailing)
- **Break-Even Protection**: Auto-moves SL to entry + commission at +1.5% profit
- **Partial Closes**: 
  - TP1: Closes 50% of position at +2%
  - TP2: Closes remaining 50% at +5%
- **Slippage Protection**: Rejects orders with >0.1% slippage

### 3. Professional Analytics
- **Win Rate Calculator**: Tracks winning vs losing trades percentage
- **Average Profit/Loss**: Calculates avg profit per winning trade, avg loss per losing trade
- **Maximum Drawdown**: Monitors largest peak-to-trough decline
- **Profit Factor**: Ratio of total profits to total losses
- **Equity Curve**: Visual 24-hour balance growth chart
- **Consecutive Streaks**: Tracks current winning/losing streaks

### 4. Portfolio Management
- **Realized Profit**: Total profit from closed positions
- **Unrealized PnL**: Current profit/loss from open positions
- **Total Portfolio Value**: Combined realized + unrealized gains
- **Position Tracking**: Detailed view of entry/current/exit prices

### 5. Notification System
- **Telegram Integration**: Instant alerts on position open/close
- **Discord Webhooks**: Rich embeds with trade details
- **Trade Summaries**: P&L, entry/exit prices, remaining balance
- **Break-Even Alerts**: Notification when risk reaches zero

### 6. Forensic Trade Logs
Each trade records:
- Entry timestamp and reason (strategy name)
- Slippage amount
- Final exit price
- Trade duration (seconds)
- Full P&L breakdown

## 📊 Dashboard Components

### Price Ticker
```jsx
<PriceTicker ticker="BTCUSD" api={api} token={token} />
```
Real-time price with color changes

### Connection Status
```jsx
<ConnectionStatus api={api} />
```
LED indicator (green=connected, red=disconnected)

### Equity Curve
```jsx
<EquityCurve api={api} token={token} />
```
Sparkline chart showing 24h balance growth

## 🔧 Configuration

### Environment Variables
```bash
# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Discord (Optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Get Telegram Credentials
1. Message @BotFather on Telegram
2. Create new bot with `/newbot`
3. Copy the bot token
4. Message your bot, then visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Find your `chat_id` in the JSON response

### Get Discord Webhook
1. Go to Server Settings > Integrations > Webhooks
2. Create New Webhook
3. Copy Webhook URL

## 🚀 API Endpoints

### Advanced Analytics
```
GET /dashboard/analytics
GET /dashboard/equity-curve?hours=24
GET /dashboard/connection-status
GET /dashboard/realtime-prices
GET /dashboard/partial-closes/<position_id>
GET /dashboard/trade-logs
```

## 📈 Risk Management Flow

```
New Position Opened
    ↓
Trailing Stop Activated (follows price up)
    ↓
Price reaches +1.5% → Break-Even Protection (SL = Entry + Fee)
    ↓
Price reaches +2% → TP1 Triggered (Close 50%)
    ↓
Price reaches +5% → TP2 Triggered (Close remaining 50%)
```

## 🛡️ Slippage Protection

Before executing any order:
1. Compare alert price vs current market price
2. Calculate slippage: `|current - alert| / alert`
3. If slippage > 0.1%, reject order
4. Log rejection reason

## 📊 Database Schema

### New Tables
- `partial_closes`: Records each partial TP execution
- `trade_logs`: Forensic logs for every trade
- `connection_status`: Real-time connection health
- `equity_curve`: Historical balance snapshots

### Updated Tables
- `positions`: Added columns for trailing_stop, break_even_active, tp1_closed, tp2_closed, remaining_quantity
- `trading_stats`: Added avg_profit, avg_loss, max_drawdown, consecutive_wins/losses

## 🎨 UI/UX Features

- **Color-Coded P&L**: Green for profits, red for losses
- **Real-Time Updates**: Dashboard auto-refreshes every 10 seconds
- **Manual Refresh Button**: Force immediate data reload
- **Last Update Timestamp**: Shows when data was last fetched
- **Responsive Tables**: Professional layout with sorting capabilities
- **Visual Indicators**: Badges, LED lights, sparklines

## 🔐 Security

- JWT authentication for all endpoints
- Token expiration handling
- SQL injection protection (parameterized queries)
- Input validation on all endpoints
- CORS configuration for production

## 📦 Tech Stack

**Backend:**
- Flask 3.0 (Python web framework)
- SQLite (Database)
- WebSockets (Real-time data)
- yfinance (Market data fallback)
- requests (HTTP client for APIs)

**Frontend:**
- React 18
- Vite 5
- CSS Modules
- SVG for charts

**Services:**
- Binance WebSocket API (Real-time prices)
- Telegram Bot API (Notifications)
- Discord Webhooks (Notifications)
- Railway (Backend hosting)
- Vercel (Frontend hosting)

## 🚦 Getting Started

1. Clone repo
2. Install dependencies:
   ```bash
   cd backend && pip install -r requirements.txt
   cd ../frontend && npm install
   ```
3. Configure environment variables (optional notifications)
4. Run migrations:
   ```bash
   python migrations/add_risk_management.py
   ```
5. Start services:
   ```bash
   cd backend && python app.py
   cd ../frontend && npm run dev
   ```

## 📚 Documentation

- [TradingEngine API](backend/services/trading_engine.py)
- [WebSocket Service](backend/services/websocket_service.py)
- [Analytics Service](backend/services/analytics_service.py)
- [Notification Service](backend/services/notification_service.py)

## 🎯 Roadmap

- [ ] Multi-timeframe analysis
- [ ] Custom strategy builder
- [ ] Backtesting engine
- [ ] Options trading support
- [ ] Copy trading feature
- [ ] Mobile app (React Native)

## 📞 Support

For issues or questions, open an issue on GitHub.

---

Built with ❤️ by Professional Quant Developers
