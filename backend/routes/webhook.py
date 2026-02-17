from flask import Blueprint, request, jsonify
from auth_utils import token_required
from database import get_db_connection
from datetime import datetime
import json

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/test', methods=['GET', 'POST'], strict_slashes=False)
def webhook_test():
    """Simple test endpoint to verify webhook is reachable"""
    return jsonify({
        'status': 'OK',
        'message': 'Webhook endpoint is working',
        'method': request.method,
        'timestamp': datetime.now().isoformat()
    }), 200

@webhook_bp.route('/recent', methods=['GET'], strict_slashes=False)
def recent_webhooks():
    """Get recent webhooks - PUBLIC endpoint for debugging"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, payload, received_at
            FROM webhooks 
            ORDER BY received_at DESC
            LIMIT 20
        ''')
        
        webhooks = cursor.fetchall()
        conn.close()
        
        webhooks_list = []
        for webhook in webhooks:
            try:
                payload_data = json.loads(webhook['payload'])
            except:
                payload_data = webhook['payload']
            
            webhooks_list.append({
                'id': webhook['id'],
                'payload': payload_data,
                'received_at': webhook['received_at']
            })
        
        return jsonify({
            'count': len(webhooks_list),
            'webhooks': webhooks_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'count': 0,
            'webhooks': []
        }), 200

@webhook_bp.route('/', methods=['POST', 'GET'], strict_slashes=False)
@webhook_bp.route('', methods=['POST', 'GET'], strict_slashes=False)
def tradingview_webhook():
    """
    TradingView webhook endpoint - accepts any JSON payload
    Logs all incoming webhooks to database
    """
    # Log everything for debugging
    print(f"🔔 WEBHOOK RECEIVED - Method: {request.method}")
    print(f"📋 Headers: {dict(request.headers)}")
    print(f"📦 Raw Data: {request.data}")
    print(f"🔍 Content-Type: {request.content_type}")
    
    # Accept both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        # Try to get raw data
        try:
            data = json.loads(request.data.decode('utf-8'))
        except:
            data = {
                'raw_message': request.data.decode('utf-8'),
                'content_type': request.content_type,
                'method': request.method
            }
    
    if not data:
        data = {'empty': True, 'method': request.method}
    
    # Save webhook to database
    webhook_id = None
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
    
    # Process trading signal if bot is active in DEMO mode
    try:
        process_demo_trade(data)
    except Exception as e:
        print(f"⚠️ Error processing demo trade: {str(e)}")
    
    return jsonify({
        'status': 'received',
        'message': 'Webhook processed successfully',
        'data': data,
        'webhook_id': webhook_id
    }), 200


def process_demo_trade(webhook_data):
    """Process trading signal in DEMO mode (without real broker API)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all active users with demo mode enabled
    cursor.execute('''
        SELECT user_id, max_position_size, stop_loss_percent, take_profit_percent
        FROM bot_config 
        WHERE is_active = 1 AND demo_mode = 1
    ''')
    
    active_bots = cursor.fetchall()
    
    if not active_bots:
        conn.close()
        print("ℹ️ No active bots in demo mode")
        return
    
    # Extract trading signal from webhook
    ticker = webhook_data.get('ticker', 'UNKNOWN')
    price = float(webhook_data.get('price', 0))
    signal = webhook_data.get('signal', '').upper()
    
    if not ticker or not price or signal not in ['BUY', 'SELL']:
        conn.close()
        print(f"⚠️ Invalid trading signal: {webhook_data}")
        return
    
    # Create demo positions for each active bot
    for bot in active_bots:
        user_id = bot['user_id']
        position_size = bot['max_position_size']
        
        # Calculate quantity based on position size
        quantity = round(position_size / price, 2)
        
        # Create demo position
        cursor.execute('''
            INSERT INTO positions (
                user_id, symbol, side, quantity, entry_price, 
                current_price, pnl, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, ticker, signal, quantity, price,
            price, 0.0, 'open'
        ))
        
        # Update stats
        cursor.execute('''
            UPDATE trading_stats 
            SET total_trades = total_trades + 1
            WHERE user_id = ?
        ''', (user_id,))
        
        print(f"💰 DEMO Trade Created - User {user_id}: {signal} {quantity} {ticker} @ ${price}")
    
    conn.commit()
    conn.close()
