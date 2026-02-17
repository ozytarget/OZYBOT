from flask import Blueprint, request, jsonify
from auth_utils import token_required
from database import get_db_connection
from datetime import datetime
import json
from services.cooldown_manager import cooldown_manager
from services.slippage_tracker import slippage_tracker

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
        SELECT user_id, max_position_size, stop_loss_percent, take_profit_percent, auto_close_enabled
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
    
    if not ticker or not price:
        conn.close()
        print(f"⚠️ Invalid trading signal: {webhook_data}")
        return
    
    # ✅ CHECK COOLDOWN BEFORE PROCESSING SIGNAL
    cooldown_status = cooldown_manager.is_ticker_in_cooldown(ticker)
    if cooldown_status['in_cooldown']:
        print(f"❄️ COOLDOWN ACTIVE - {ticker} is in cooldown for {cooldown_status['time_remaining_minutes']} minutes. Skipping signal.")
        conn.close()
        return
    
    # Process for each active bot
    for bot in active_bots:
        user_id = bot['user_id']
        position_size = bot['max_position_size']
        stop_loss_pct = bot['stop_loss_percent']
        take_profit_pct = bot['take_profit_percent']
        
        # First, update existing open positions for this ticker and check SL/TP
        cursor.execute('''
            SELECT id, symbol, side, quantity, entry_price, current_price, pnl
            FROM positions 
            WHERE user_id = ? AND symbol = ? AND status = 'open'
        ''', (user_id, ticker))
        
        open_positions = cursor.fetchall()
        
        for pos in open_positions:
            old_price = pos['current_price'] or pos['entry_price']
            
            # Update current price and calculate new PnL
            if pos['side'] == 'BUY':
                # For long positions: profit when price goes up
                pnl = (price - pos['entry_price']) * pos['quantity']
                pnl_percent = ((price - pos['entry_price']) / pos['entry_price']) * 100
            else:  # SELL
                # For short positions: profit when price goes down
                pnl = (pos['entry_price'] - price) * pos['quantity']
                pnl_percent = ((pos['entry_price'] - price) / pos['entry_price']) * 100
            
            # Update position with new price and PnL
            cursor.execute('''
                UPDATE positions 
                SET current_price = ?, pnl = ?
                WHERE id = ?
            ''', (price, pnl, pos['id']))
            
            # Check if Stop Loss or Take Profit is triggered (only if auto-close is enabled)
            should_close = False
            close_reason = ""
            auto_close_enabled = bot['auto_close_enabled']
            
            if auto_close_enabled:
                if pnl_percent <= -stop_loss_pct:
                    should_close = True
                    close_reason = f"Stop Loss ({pnl_percent:.2f}%)"
                elif pnl_percent >= take_profit_pct:
                    should_close = True
                    close_reason = f"Take Profit ({pnl_percent:.2f}%)"
            
            if should_close:
                # Close the position
                cursor.execute('''
                    UPDATE positions 
                    SET status = 'closed', closed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (pos['id'],))
                
                # ✅ ACTIVATE COOLDOWN IF STOP LOSS
                if "Stop Loss" in close_reason:
                    cooldown_result = cooldown_manager.activate_cooldown(
                        ticker=ticker,
                        reason=f"Stop Loss triggered at ${price}",
                        duration_minutes=60
                    )
                    print(f"❄️ COOLDOWN ACTIVATED - {ticker} locked for 60 minutes after Stop Loss")
                
                # Update trading stats
                if pnl >= 0:
                    cursor.execute('''
                        UPDATE trading_stats 
                        SET winning_trades = winning_trades + 1,
                            total_profit = total_profit + ?
                        WHERE user_id = ?
                    ''', (pnl, user_id))
                else:
                    cursor.execute('''
                        UPDATE trading_stats 
                        SET losing_trades = losing_trades + 1,
                            total_profit = total_profit + ?
                        WHERE user_id = ?
                    ''', (pnl, user_id))
                
                print(f"🔴 CLOSED Position - User {user_id}: {pos['symbol']} ${price} | {close_reason} | PnL: ${pnl:.2f}")
            else:
                print(f"📊 UPDATED Position - User {user_id}: {pos['symbol']} ${old_price} → ${price} | PnL: ${pnl:.2f} ({pnl_percent:+.2f}%)")
        
        # Create new position if signal is provided
        if signal in ['BUY', 'SELL']:
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
            
            position_id = cursor.lastrowid
            
            # ✅ RECORD SLIPPAGE (TradingView expected price vs actual execution)
            # In DEMO mode, expected = actual, but in LIVE this would capture real slippage
            try:
                slippage_tracker.record_slippage(
                    position_id=position_id,
                    ticker=ticker,
                    expected_price=price,  # From TradingView
                    actual_price=price     # In DEMO, same. In LIVE, broker execution price
                )
            except Exception as e:
                print(f"⚠️ Error recording slippage: {str(e)}")
            
            # Update stats
            cursor.execute('''
                UPDATE trading_stats 
                SET total_trades = total_trades + 1
                WHERE user_id = ?
            ''', (user_id,))
            
            print(f"💰 OPENED Position - User {user_id}: {signal} {quantity} {ticker} @ ${price}")
    
    conn.commit()
    conn.close()
    
    conn.commit()
    conn.close()
