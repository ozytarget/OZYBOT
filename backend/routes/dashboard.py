from flask import Blueprint, request, jsonify
from auth_utils import token_required
from database import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get trading stats
    cursor.execute('''
        SELECT total_trades, winning_trades, losing_trades, total_profit
        FROM trading_stats WHERE user_id = ?
    ''', (user_id,))
    stats = cursor.fetchone()
    
    # Get bot status
    cursor.execute('SELECT is_active FROM bot_config WHERE user_id = ?', (user_id,))
    bot_config = cursor.fetchone()
    
    # Get open positions count
    cursor.execute('''
        SELECT COUNT(*) as open_count FROM positions 
        WHERE user_id = ? AND status = 'open'
    ''', (user_id,))
    positions_data = cursor.fetchone()
    
    conn.close()
    
    if not stats:
        return jsonify({'error': 'Stats not found'}), 404
    
    win_rate = 0
    if stats['total_trades'] > 0:
        win_rate = (stats['winning_trades'] / stats['total_trades']) * 100
    
    return jsonify({
        'total_trades': stats['total_trades'],
        'winning_trades': stats['winning_trades'],
        'losing_trades': stats['losing_trades'],
        'win_rate': round(win_rate, 2),
        'total_profit': stats['total_profit'],
        'bot_active': bool(bot_config['is_active']),
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
        conn.close()
        return jsonify({'error': 'Bot config not found'}), 404
    
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
