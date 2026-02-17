import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import init_db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.settings import settings_bp
from routes.webhook import webhook_bp

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
        from migrations.repair_database import repair_database
        repair_database()
    except Exception as e:
        print(f"⚠️ Migration warning: {str(e)}")

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(settings_bp, url_prefix='/settings')
app.register_blueprint(webhook_bp, url_prefix='/webhook')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({
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
