from flask import Blueprint, request, jsonify
from database import get_db_connection
from auth_utils import hash_password, verify_password, generate_token, token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'User already exists'}), 409
    
    # Create new user
    password_hash = hash_password(password)
    cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)',
                   (email, password_hash))
    user_id = cursor.lastrowid
    
    # Initialize bot config
    cursor.execute('INSERT INTO bot_config (user_id) VALUES (?)', (user_id,))
    
    # Initialize broker settings
    cursor.execute('INSERT INTO broker_settings (user_id) VALUES (?)', (user_id,))
    
    # Initialize trading stats
    cursor.execute('INSERT INTO trading_stats (user_id) VALUES (?)', (user_id,))
    
    conn.commit()
    conn.close()
    
    token = generate_token(user_id)
    
    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': {'id': user_id, 'email': email}
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, email, password_hash FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(password, user['password_hash']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = generate_token(user['id'])
    
    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'email': user['email']}
    }), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, email, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user['id'],
        'email': user['email'],
        'created_at': user['created_at']
    }), 200
