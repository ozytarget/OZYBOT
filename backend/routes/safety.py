"""
Panic & Safety Routes
Endpoints para Kill Switch, Heartbeat, Cooldowns, Slippage
"""
from flask import Blueprint, jsonify, request
from auth_utils import token_required
from services.panic_mode import panic_service
from services.heartbeat_monitor import heartbeat_monitor
from services.cooldown_manager import cooldown_manager
from services.slippage_tracker import slippage_tracker

safety_bp = Blueprint('safety', __name__)

# ============================================================================
# PANIC MODE / KILL SWITCH
# ============================================================================

@safety_bp.route('/panic/kill-switch', methods=['POST'])
@token_required
def trigger_kill_switch(user_id):
    """
    🚨 KILL SWITCH: Cierra todas las posiciones y desactiva el bot
    
    Body (opcional):
        {
            "reason": "Manual panic by user"
        }
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Manual kill switch activation')
        
        result = panic_service.execute_kill_switch(user_id=user_id, reason=reason)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@safety_bp.route('/panic/disable-webhook', methods=['POST'])
@token_required
def emergency_disable_webhook(user_id):
    """
    Desactiva el webhook globalmente (no entran más señales)
    """
    result = panic_service.emergency_disable_webhook()
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@safety_bp.route('/panic/history', methods=['GET'])
@token_required
def get_panic_history(user_id):
    """
    Obtiene histórico de activaciones del kill switch
    """
    limit = request.args.get('limit', 10, type=int)
    result = panic_service.get_panic_history(user_id=user_id, limit=limit)
    
    return jsonify(result), 200

# ============================================================================
# HEARTBEAT MONITOR
# ============================================================================

@safety_bp.route('/heartbeat/status', methods=['GET'])
def get_heartbeat_status():
    """
    Obtiene el estado del heartbeat monitor (no requiere auth para monitoring externo)
    """
    status = heartbeat_monitor.get_status()
    return jsonify(status), 200

@safety_bp.route('/heartbeat/ping', methods=['POST'])
def ping_heartbeat():
    """
    Manual heartbeat ping (para testing)
    """
    heartbeat_monitor.update_heartbeat()
    return jsonify({
        'success': True,
        'message': 'Heartbeat updated',
        'timestamp': heartbeat_monitor.last_heartbeat.isoformat()
    }), 200

# ============================================================================
# COOLDOWN MANAGER (Anti-Whipsaw)
# ============================================================================

@safety_bp.route('/cooldowns/active', methods=['GET'])
@token_required
def get_active_cooldowns(user_id):
    """
    Lista todos los tickers actualmente en cooldown
    """
    result = cooldown_manager.get_active_cooldowns()
    return jsonify(result), 200

@safety_bp.route('/cooldowns/check/<ticker>', methods=['GET'])
@token_required
def check_ticker_cooldown(user_id, ticker):
    """
    Verifica si un ticker específico está en cooldown
    """
    result = cooldown_manager.is_ticker_in_cooldown(ticker)
    return jsonify(result), 200

@safety_bp.route('/cooldowns/activate', methods=['POST'])
@token_required
def activate_cooldown(user_id):
    """
    Activa cooldown manualmente para un ticker
    
    Body:
        {
            "ticker": "AMZN",
            "duration_minutes": 60,
            "reason": "Manual cooldown"
        }
    """
    data = request.get_json()
    
    ticker = data.get('ticker')
    duration = data.get('duration_minutes', 60)
    reason = data.get('reason', 'Manual activation')
    
    if not ticker:
        return jsonify({'error': 'ticker is required'}), 400
    
    result = cooldown_manager.activate_cooldown(ticker, reason, duration)
    return jsonify(result), 200

@safety_bp.route('/cooldowns/deactivate/<ticker>', methods=['POST'])
@token_required
def deactivate_cooldown(user_id, ticker):
    """
    Desactiva cooldown manualmente para un ticker
    """
    result = cooldown_manager.deactivate_cooldown(ticker)
    return jsonify(result), 200

# ============================================================================
# SLIPPAGE TRACKER
# ============================================================================

@safety_bp.route('/slippage/stats', methods=['GET'])
@token_required
def get_slippage_stats(user_id):
    """
    Obtiene estadísticas de slippage
    
    Query params:
        ticker: Filtrar por ticker (opcional)
        days: Últimos N días (default: 7)
    """
    ticker = request.args.get('ticker', None)
    days = request.args.get('days', 7, type=int)
    
    result = slippage_tracker.get_slippage_stats(ticker=ticker, days=days)
    return jsonify(result), 200

@safety_bp.route('/slippage/events', methods=['GET'])
@token_required
def get_slippage_events(user_id):
    """
    Obtiene últimos eventos de slippage registrados
    """
    limit = request.args.get('limit', 20, type=int)
    result = slippage_tracker.get_recent_slippage_events(limit=limit)
    return jsonify(result), 200

@safety_bp.route('/slippage/broker-quality/<ticker>', methods=['GET'])
@token_required
def check_broker_quality(user_id, ticker):
    """
    Analiza la calidad del broker para un ticker específico
    """
    result = slippage_tracker.check_broker_quality(ticker)
    return jsonify(result), 200

# ============================================================================
# SYSTEM HEALTH
# ============================================================================

@safety_bp.route('/health/full-report', methods=['GET'])
def get_full_health_report():
    """
    Reporte completo de salud del sistema (para monitoring externo)
    """
    try:
        heartbeat_status = heartbeat_monitor.get_status()
        cooldowns = cooldown_manager.get_active_cooldowns()
        
        return jsonify({
            'success': True,
            'heartbeat': heartbeat_status,
            'cooldowns': cooldowns,
            'timestamp': heartbeat_monitor.last_heartbeat.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
