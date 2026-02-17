from flask import Blueprint, request, jsonify
from auth_utils import token_required
from database import get_db_connection
from datetime import datetime

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/', methods=['POST'], strict_slashes=False)
@webhook_bp.route('', methods=['POST'], strict_slashes=False)
def tradingview_webhook():
    """
    TradingView webhook endpoint
    Expected payload: {
        "secret": "your-webhook-secret",
        "symbol": "BTCUSD",
        "action": "buy" or "sell",
        "price": 50000.00,
        "quantity": 0.1
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Basic validation
    required_fields = ['symbol', 'action', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # In production, verify webhook secret
    # if data.get('secret') != Config.WEBHOOK_SECRET:
    #     return jsonify({'error': 'Invalid secret'}), 401
    
    # Log the webhook (in production, process the trade)
    print(f"Webhook received: {data}")
    
    # Here you would implement the actual trading logic
    # For now, just acknowledge receipt
    
    return jsonify({
        'status': 'received',
        'message': 'Webhook processed successfully',
        'data': data
    }), 200
