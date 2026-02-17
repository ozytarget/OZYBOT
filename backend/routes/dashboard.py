from flask import Blueprint, request, jsonify
from auth_utils import token_required
from database import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get trading stats - create if missing
    cursor.execute('''
        SELECT total_trades, winning_trades, losing_trades, total_profit
        FROM trading_stats WHERE user_id = ?
    ''', (user_id,))
    stats = cursor.fetchone()
    
    if not stats:
        # Create trading stats if missing
        cursor.execute('INSERT INTO trading_stats (user_id) VALUES (?)', (user_id,))
        conn.commit()
        cursor.execute('''
            SELECT total_trades, winning_trades, losing_trades, total_profit
            FROM trading_stats WHERE user_id = ?
        ''', (user_id,))
        stats = cursor.fetchone()
    
    # Get bot status - create if missing
    cursor.execute('SELECT is_active, demo_mode FROM bot_config WHERE user_id = ?', (user_id,))
    bot_config = cursor.fetchone()
    
    if not bot_config:
        # Create bot config if missing
        cursor.execute('INSERT INTO bot_config (user_id, is_active, demo_mode) VALUES (?, ?, ?)',
                       (user_id, 0, 1))
        conn.commit()
        bot_config = {'is_active': 0, 'demo_mode': 1}
    
    # Get open positions count
    cursor.execute('''
        SELECT COUNT(*) as open_count FROM positions 
        WHERE user_id = ? AND status = 'open'
    ''', (user_id,))
    positions_data = cursor.fetchone()
    
    conn.close()
    
    win_rate = 0
    if stats['total_trades'] > 0:
        win_rate = (stats['winning_trades'] / stats['total_trades']) * 100
    
    # Handle demo_mode field - might not exist in old databases
    demo_mode = bot_config.get('demo_mode', 1) if isinstance(bot_config, dict) else 1
    try:
        demo_mode = bool(bot_config['demo_mode'])
    except (KeyError, TypeError):
        demo_mode = True
    
    return jsonify({
        'total_trades': stats['total_trades'],
        'winning_trades': stats['winning_trades'],
        'losing_trades': stats['losing_trades'],
        'win_rate': round(win_rate, 2),
        'total_profit': stats['total_profit'],
        'bot_active': bool(bot_config['is_active']),
        'demo_mode': demo_mode,
        'open_positions': positions_data['open_count']
    }), 200

@dashboard_bp.route('/positions', methods=['GET'])
@token_required
def get_positions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, symbol, side, quantity, entry_price, current_price, 
               pnl, status, opened_at, closed_at
        FROM positions 
        WHERE user_id = ?
        ORDER BY opened_at DESC
    ''', (user_id,))
    
    positions = cursor.fetchall()
    conn.close()
    
    positions_list = []
    for pos in positions:
        positions_list.append({
            'id': pos['id'],
            'symbol': pos['symbol'],
            'side': pos['side'],
            'quantity': pos['quantity'],
            'entry_price': pos['entry_price'],
            'current_price': pos['current_price'],
            'pnl': pos['pnl'],
            'status': pos['status'],
            'opened_at': pos['opened_at'],
            'closed_at': pos['closed_at']
        })
    
    return jsonify({'positions': positions_list}), 200

@dashboard_bp.route('/toggle-bot', methods=['POST'])
@token_required
def toggle_bot(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current status
    cursor.execute('SELECT is_active FROM bot_config WHERE user_id = ?', (user_id,))
    config = cursor.fetchone()
    
    if not config:
        # Create bot config if it doesn't exist
        print(f"Creating bot config for user {user_id}")
        cursor.execute('INSERT INTO bot_config (user_id, is_active, demo_mode) VALUES (?, ?, ?)',
                       (user_id, 1, 1))  # Start active in demo mode
        
        # Also create trading stats if missing
        cursor.execute('SELECT id FROM trading_stats WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO trading_stats (user_id) VALUES (?)', (user_id,))
        
        # Also create broker settings if missing
        cursor.execute('SELECT id FROM broker_settings WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO broker_settings (user_id) VALUES (?)', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Bot config created and activated',
            'is_active': True
        }), 200
    
    # Toggle status
    new_status = not config['is_active']
    cursor.execute('UPDATE bot_config SET is_active = ? WHERE user_id = ?',
                   (new_status, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Bot status updated',
        'is_active': new_status
    }), 200

@dashboard_bp.route('/webhooks', methods=['GET'])
@token_required
def get_webhooks(user_id):
    """Get recent webhooks received from TradingView"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get last 50 webhooks
    cursor.execute('''
        SELECT id, payload, received_at
        FROM webhooks 
        ORDER BY received_at DESC
        LIMIT 50
    ''')
    
    webhooks = cursor.fetchall()
    conn.close()
    
    webhooks_list = []
    for webhook in webhooks:
        webhooks_list.append({
            'id': webhook['id'],
            'payload': webhook['payload'],
            'received_at': webhook['received_at']
        })
    
    return jsonify({'webhooks': webhooks_list}), 200

@dashboard_bp.route('/close-position/<int:position_id>', methods=['POST'])
@token_required
def close_position(user_id, position_id):
    """Manually close a position"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get position and verify ownership
    cursor.execute('''
        SELECT id, symbol, side, quantity, entry_price, current_price, pnl, status
        FROM positions 
        WHERE id = ? AND user_id = ?
    ''', (position_id, user_id))
    
    position = cursor.fetchone()
    
    if not position:
        conn.close()
        return jsonify({'error': 'Position not found'}), 404
    
    if position['status'] != 'open':
        conn.close()
        return jsonify({'error': 'Position already closed'}), 400
    
    # Close the position
    cursor.execute('''
        UPDATE positions 
        SET status = 'closed', closed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (position_id,))
    
    # Update trading stats
    pnl = position['pnl'] or 0.0
    
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
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Position closed successfully',
        'position_id': position_id,
        'pnl': pnl,
        'symbol': position['symbol']
    }), 200
