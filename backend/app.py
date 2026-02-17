import os
import atexit
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import init_db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.settings import settings_bp
from routes.webhook import webhook_bp
from routes.safety import safety_bp
from services import (
    price_monitor,
    trading_engine,
    realtime_price_service,
    notification_service,
    analytics_service,
    panic_service,
    heartbeat_monitor,
    cooldown_manager,
    slippage_tracker
)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize database
with app.app_context():
    init_db()
    # Run migrations
    try:
        from migrations.add_demo_mode import run_migration
        run_migration()
        from migrations.add_auto_close import run_migration as run_auto_close_migration
        run_auto_close_migration()
        from migrations.repair_database import repair_database
        repair_database()
        from migrations.add_risk_management import run_migration as run_risk_migration
        run_risk_migration()
        from migrations.add_professional_safety import run_migration as run_safety_migration
        run_safety_migration()
    except Exception as e:
        print(f"⚠️ Migration warning: {str(e)}")

# Start Professional Trading Services
print("🚀 Iniciando Price Monitor...")
try:
    price_monitor.start()
except Exception as e:
    print(f"⚠️ Error iniciando Price Monitor: {str(e)}")

print("🔌 Iniciando WebSocket Service (Real-Time Prices)...")
try:
    realtime_price_service.start()
except Exception as e:
    print(f"⚠️ Error iniciando WebSocket Service: {str(e)}")

print("💓 Iniciando Heartbeat Monitor...")
try:
    heartbeat_monitor.start()
except Exception as e:
    print(f"⚠️ Error iniciando Heartbeat Monitor: {str(e)}")

print("✅ Servicios profesionales iniciados")

# Clean shutdown
def cleanup():
    try:
        print("🛑 Deteniendo servicios...")
        price_monitor.stop()
        realtime_price_service.stop()
    except Exception as e:
        print(f"⚠️ Error deteniendo servicios: {str(e)}")

atexit.register(cleanup)
app.register_blueprint(safety_bp, url_prefix='/safety')

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(settings_bp, url_prefix='/settings')
app.register_blueprint(webhook_bp, url_prefix='/webhook')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():2.0.0-PRO',
        'endpoints': {
            'auth': '/auth/register, /auth/login, /auth/me',
            'dashboard': '/dashboard/stats, /dashboard/positions, /dashboard/toggle-bot',
            'settings': '/settings/config, /settings/broker',
            'webhook': '/webhook',
            'safety': '/safety/panic/kill-switch, /safety/heartbeat/status, /safety/cooldowns/active, /safety/slippage/stats
        'message': 'Trading Bot API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/auth/register, /auth/login, /auth/me',
            'dashboard': '/dashboard/stats, /dashboard/positions, /dashboard/toggle-bot',
            'settings': '/settings/config, /settings/broker',
            'webhook': '/webhook'
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', Config.PORT))
    app.run(host='0.0.0.0', port=port, debug=(Config.FLASK_ENV == 'development'))
