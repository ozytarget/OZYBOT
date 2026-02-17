from flask import Blueprint, request, jsonify
from auth_utils import token_required
from database import get_db_connection

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/config', methods=['GET'])
@token_required
def get_config(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT risk_level, max_position_size, stop_loss_percent, take_profit_percent
        FROM bot_config WHERE user_id = ?
    ''', (user_id,))
    
    config = cursor.fetchone()
    conn.close()
    
    if not config:
        return jsonify({'error': 'Config not found'}), 404
    
    return jsonify({
        'risk_level': config['risk_level'],
        'max_position_size': config['max_position_size'],
        'stop_loss_percent': config['stop_loss_percent'],
        'take_profit_percent': config['take_profit_percent']
    }), 200

@settings_bp.route('/config', methods=['PUT'])
@token_required
def update_config(user_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update only provided fields
    if 'risk_level' in data:
        cursor.execute('UPDATE bot_config SET risk_level = ? WHERE user_id = ?',
                       (data['risk_level'], user_id))
    
    if 'max_position_size' in data:
        cursor.execute('UPDATE bot_config SET max_position_size = ? WHERE user_id = ?',
                       (data['max_position_size'], user_id))
    
    if 'stop_loss_percent' in data:
        cursor.execute('UPDATE bot_config SET stop_loss_percent = ? WHERE user_id = ?',
                       (data['stop_loss_percent'], user_id))
    
    if 'take_profit_percent' in data:
        cursor.execute('UPDATE bot_config SET take_profit_percent = ? WHERE user_id = ?',
                       (data['take_profit_percent'], user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Config updated successfully'}), 200

@settings_bp.route('/broker', methods=['GET'])
@token_required
def get_broker(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT broker_name, is_connected
        FROM broker_settings WHERE user_id = ?
    ''', (user_id,))
    
    broker = cursor.fetchone()
    conn.close()
    
    if not broker:
        return jsonify({'error': 'Broker settings not found'}), 404
    
    return jsonify({
        'broker_name': broker['broker_name'],
        'is_connected': bool(broker['is_connected'])
    }), 200

@settings_bp.route('/broker', methods=['PUT'])
@token_required
def update_broker(user_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update broker settings
    if 'broker_name' in data:
        cursor.execute('UPDATE broker_settings SET broker_name = ? WHERE user_id = ?',
                       (data['broker_name'], user_id))
    
    if 'api_key' in data:
        cursor.execute('UPDATE broker_settings SET api_key = ? WHERE user_id = ?',
                       (data['api_key'], user_id))
    
    if 'api_secret' in data:
        cursor.execute('UPDATE broker_settings SET api_secret = ? WHERE user_id = ?',
                       (data['api_secret'], user_id))
    
    if 'is_connected' in data:
        cursor.execute('UPDATE broker_settings SET is_connected = ? WHERE user_id = ?',
                       (data['is_connected'], user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Broker settings updated successfully'}), 200
