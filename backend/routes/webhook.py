from flask import Blueprint, request, jsonify
from auth_utils import token_required
from database import get_db_connection
from datetime import datetime
import json

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/', methods=['POST'], strict_slashes=False)
@webhook_bp.route('', methods=['POST'], strict_slashes=False)
def tradingview_webhook():
    """
    TradingView webhook endpoint - accepts any JSON payload
    Logs all incoming webhooks to database
    """
    # Accept both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        # Try to get raw data
        try:
            data = json.loads(request.data.decode('utf-8'))
        except:
            data = {'raw_message': request.data.decode('utf-8')}
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Save webhook to database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO webhooks (payload) VALUES (?)',
            (json.dumps(data),)
        )
        conn.commit()
        webhook_id = cursor.lastrowid
        conn.close()
        
        # Log to console
        print(f"✅ Webhook #{webhook_id} received and saved: {data}")
        
    except Exception as e:
        print(f"❌ Error saving webhook: {str(e)}")
        # Still return success to TradingView
    
    # Here you would implement the actual trading logic
    # For now, just acknowledge receipt
    
    return jsonify({
        'status': 'received',
        'message': 'Webhook processed successfully',
        'data': data
    }), 200
