"""
Panic Mode Service - Kill Switch para emergencias
Cierra todas las posiciones y desactiva el bot inmediatamente
"""
import sqlite3
from datetime import datetime
from services.notification_service import notification_service

class PanicModeService:
    def __init__(self, db_path='trading_bot.db'):
        self.db_path = db_path
    
    def execute_kill_switch(self, user_id, reason="Manual panic activation"):
        """
        KILL SWITCH: Cierra todo inmediatamente
        
        1. Desactiva el bot para que no entre en nuevas posiciones
        2. Cierra todas las posiciones abiertas a mercado
        3. Registra el evento en logs
        4. Envía notificación crítica
        
        Returns:
            dict: {
                'success': bool,
                'positions_closed': int,
                'message': str,
                'errors': list
            }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            errors = []
            positions_closed = 0
            
            # PASO 1: DESACTIVAR BOT INMEDIATAMENTE
            cursor.execute("""
                UPDATE bot_config 
                SET is_active = 0 
                WHERE user_id = ?
            """, (user_id,))
            
            print(f"🔴 PANIC MODE ACTIVATED - Bot desactivado para user_id={user_id}")
            
            # PASO 2: OBTENER TODAS LAS POSICIONES ABIERTAS
            cursor.execute("""
                SELECT id, symbol, side, quantity, entry_price, current_price, pnl
                FROM positions
                WHERE user_id = ? AND status = 'open'
            """, (user_id,))
            
            open_positions = cursor.fetchall()
            
            if not open_positions:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'positions_closed': 0,
                    'message': 'Bot desactivado. No había posiciones abiertas.',
                    'errors': []
                }
            
            # PASO 3: CERRAR TODAS LAS POSICIONES (SIMULADO EN DEMO)
            for pos in open_positions:
                pos_id, symbol, side, quantity, entry_price, current_price, pnl = pos
                
                try:
                    # Precio de cierre = current_price o entry_price si no hay current
                    exit_price = current_price if current_price else entry_price
                    
                    # Cerrar posición
                    cursor.execute("""
                        UPDATE positions 
                        SET status = 'closed',
                            exit_price = ?,
                            closed_at = ?,
                            close_reason = ?
                        WHERE id = ?
                    """, (exit_price, datetime.now().isoformat(), f"PANIC MODE: {reason}", pos_id))
                    
                    # Actualizar estadísticas
                    if pnl >= 0:
                        cursor.execute("""
                            UPDATE trading_stats
                            SET winning_trades = winning_trades + 1,
                                total_profit = total_profit + ?
                            WHERE user_id = ?
                        """, (pnl, user_id))
                    else:
                        cursor.execute("""
                            UPDATE trading_stats
                            SET losing_trades = losing_trades + 1,
                                total_profit = total_profit + ?
                            WHERE user_id = ?
                        """, (pnl, user_id))
                    
                    # Log del cierre
                    cursor.execute("""
                        INSERT INTO trade_logs 
                        (position_id, action, price, quantity, reason, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (pos_id, 'PANIC_CLOSE', exit_price, quantity, reason, datetime.now().isoformat()))
                    
                    positions_closed += 1
                    print(f"❌ PANIC CLOSE: {symbol} | Entry: ${entry_price:.2f} | Exit: ${exit_price:.2f} | P&L: ${pnl:.2f}")
                    
                except Exception as e:
                    error_msg = f"Error cerrando {symbol}: {str(e)}"
                    errors.append(error_msg)
                    print(f"⚠️ {error_msg}")
            
            conn.commit()
            conn.close()
            
            # PASO 4: NOTIFICACIÓN CRÍTICA
            try:
                notification_service.send_panic_alert(
                    user_id=user_id,
                    positions_closed=positions_closed,
                    reason=reason
                )
            except Exception as e:
                errors.append(f"Error enviando notificación: {str(e)}")
            
            return {
                'success': True,
                'positions_closed': positions_closed,
                'message': f'🚨 PANIC MODE: {positions_closed} posiciones cerradas. Bot desactivado.',
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'positions_closed': 0,
                'message': f'Error ejecutando kill switch: {str(e)}',
                'errors': [str(e)]
            }
    
    def emergency_disable_webhook(self):
        """
        Desactiva el webhook para que no entren nuevas señales
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE bot_config 
                SET is_active = 0
            """)
            
            conn.commit()
            conn.close()
            
            print("🔴 EMERGENCY: Webhook desactivado globalmente")
            return {'success': True, 'message': 'Webhook desactivado'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_panic_history(self, user_id, limit=10):
        """
        Obtiene historial de activaciones del panic mode
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT position_id, action, reason, created_at
                FROM trade_logs
                WHERE action = 'PANIC_CLOSE'
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            history = cursor.fetchall()
            conn.close()
            
            return {
                'success': True,
                'history': [
                    {
                        'position_id': row[0],
                        'action': row[1],
                        'reason': row[2],
                        'timestamp': row[3]
                    }
                    for row in history
                ]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Instancia global
panic_service = PanicModeService()
