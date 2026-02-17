# Trading Bot - Full Stack Application

A full-stack trading bot application with Python Flask backend and React frontend. Features include user authentication, dashboard with trading statistics, position tracking, and configurable bot settings.

## Features

- **Authentication**: User registration and login with JWT tokens
- **Dashboard**: Real-time trading statistics and position tracking
- **Bot Control**: Start/stop trading bot with one click
- **Settings**: Configure risk parameters and broker integration
- **TradingView Webhook**: Receive signals from TradingView alerts
- **SQLite Database**: Lightweight database for development

## Tech Stack

### Backend
- Python 3.x
- Flask - Web framework
- SQLite - Database
- JWT - Authentication
- bcrypt - Password hashing

### Frontend
- React 18
- Vite - Build tool
- React Router - Navigation
- Vanilla CSS - Styling

## Project Structure

```
copilot-bot/
├── backend/
│   ├── routes/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── dashboard.py     # Dashboard endpoints
│   │   ├── settings.py      # Settings endpoints
│   │   └── webhook.py       # TradingView webhook
│   ├── app.py              # Main Flask application
│   ├── auth_utils.py       # JWT & password utilities
│   ├── config.py           # Configuration
│   ├── database.py         # Database initialization
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Login.jsx    # Login/Register page
    │   │   ├── Dashboard.jsx # Dashboard page
    │   │   └── Settings.jsx  # Settings page
    │   ├── App.jsx          # Main application
    │   ├── api.js           # API client
    │   └── main.jsx         # Entry point
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from template:
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux
```

5. Update `.env` with your settings (optional for development)

6. Run the backend:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### Dashboard
- `GET /dashboard/stats` - Get trading statistics
- `GET /dashboard/positions` - Get all positions
- `POST /dashboard/toggle-bot` - Start/stop bot

### Settings
- `GET /settings/config` - Get bot configuration
- `PUT /settings/config` - Update bot configuration
- `GET /settings/broker` - Get broker settings
- `PUT /settings/broker` - Update broker settings

### Webhook
- `POST /webhook` - Receive TradingView webhooks

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Dashboard**: View your trading statistics and open positions
3. **Toggle Bot**: Start or stop the trading bot
4. **Settings**: Configure risk parameters and connect your broker
5. **TradingView Integration**: Send webhook alerts to `/webhook` endpoint

## TradingView Webhook Format

Send POST requests to `http://localhost:5000/webhook` with:

```json
{
  "symbol": "BTCUSD",
  "action": "buy",
  "price": 50000.00,
  "quantity": 0.1
}
```

## Development

- Backend auto-reloads on file changes when `FLASK_ENV=development`
- Frontend hot-reloads automatically with Vite
- Database is created automatically on first run

## Production Notes

Before deploying to production:

1. Change `SECRET_KEY` in `.env` to a strong random string
2. Update CORS settings in `app.py` to allow only your frontend domain
3. Use a production database (PostgreSQL, MySQL)
4. Set `FLASK_ENV=production`
5. Build frontend: `npm run build`
6. Serve frontend build with a web server (nginx, Apache)
7. Add webhook secret verification for TradingView

## License

MIT License - Feel free to use for personal or commercial projects.
