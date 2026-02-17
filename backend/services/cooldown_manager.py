"""
Cooldown Manager - Anti-Whipsaw Protection
Previene overtrading bloqueando tickers después de pérdidas
"""
import sqlite3
from datetime import datetime, timedelta

class CooldownManager:
    def __init__(self, db_path='trading_bot.db'):
        self.db_path = db_path
        self.cooldown_duration = 60  # minutos por defecto
    
    def activate_cooldown(self, ticker, reason="Stop Loss hit", duration_minutes=60):
        """
        Activa cooldown para un ticker específico
        
        Args:
            ticker: Symbol del activo (AMZN, BTCUSD, etc)
            reason: Razón del cooldown (SL, Manual, etc)
            duration_minutes: Duración del bloqueo en minutos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cooldown_until = datetime.now() + timedelta(minutes=duration_minutes)
            
            cursor.execute("""
                INSERT OR REPLACE INTO ticker_cooldowns
                (ticker, activated_at, cooldown_until, reason, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (ticker, datetime.now().isoformat(), cooldown_until.isoformat(), reason))
            
            conn.commit()
            conn.close()
            
            print(f"🧊 COOLDOWN ACTIVADO: {ticker} bloqueado hasta {cooldown_until.strftime('%H:%M:%S')} ({duration_minutes} min)")
            
            return {
                'success': True,
                'ticker': ticker,
                'cooldown_until': cooldown_until.isoformat(),
                'duration_minutes': duration_minutes
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_ticker_in_cooldown(self, ticker):
        """
        Verifica si un ticker está actualmente en cooldown
        
        Returns:
            dict: {
                'in_cooldown': bool,
                'reason': str,
                'time_remaining_minutes': int
            }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cooldown_until, reason
                FROM ticker_cooldowns
                WHERE ticker = ? AND is_active = 1
                ORDER BY cooldown_until DESC
                LIMIT 1
            """, (ticker,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {
                    'in_cooldown': False,
                    'reason': None,
                    'time_remaining_minutes': 0
                }
            
            cooldown_until_str, reason = result
            cooldown_until = datetime.fromisoformat(cooldown_until_str)
            
            # Verificar si el cooldown ya expiró
            if datetime.now() >= cooldown_until:
                self.deactivate_cooldown(ticker)
                return {
                    'in_cooldown': False,
                    'reason': None,
                    'time_remaining_minutes': 0
                }
            
            # Cooldown activo
            time_remaining = cooldown_until - datetime.now()
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            
            return {
                'in_cooldown': True,
                'reason': reason,
                'time_remaining_minutes': minutes_remaining,
                'cooldown_until': cooldown_until.isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Error verificando cooldown: {str(e)}")
            return {
                'in_cooldown': False,
                'error': str(e)
            }
    
    def deactivate_cooldown(self, ticker):
        """
        Desactiva manualmente el cooldown de un ticker
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ticker_cooldowns
                SET is_active = 0
                WHERE ticker = ?
            """, (ticker,))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Cooldown removido: {ticker}")
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_active_cooldowns(self):
        """
        Obtiene todos los tickers actualmente en cooldown
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ticker, activated_at, cooldown_until, reason
                FROM ticker_cooldowns
                WHERE is_active = 1 AND cooldown_until > datetime('now')
                ORDER BY cooldown_until ASC
            """)
            
            cooldowns = cursor.fetchall()
            conn.close()
            
            result = []
            for ticker, activated_at, cooldown_until, reason in cooldowns:
                cooldown_until_dt = datetime.fromisoformat(cooldown_until)
                time_remaining = cooldown_until_dt - datetime.now()
                minutes_remaining = int(time_remaining.total_seconds() / 60)
                
                result.append({
                    'ticker': ticker,
                    'activated_at': activated_at,
                    'cooldown_until': cooldown_until,
                    'reason': reason,
                    'minutes_remaining': minutes_remaining
                })
            
            return {
                'success': True,
                'cooldowns': result,
                'count': len(result)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'cooldowns': []
            }
    
    def cleanup_expired_cooldowns(self):
        """
        Limpia cooldowns expirados de la base de datos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ticker_cooldowns
                SET is_active = 0
                WHERE cooldown_until < datetime('now')
            """)
            
            rows_updated = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_updated > 0:
                print(f"🧹 Cooldowns expirados limpiados: {rows_updated}")
            
            return {'success': True, 'cleaned': rows_updated}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Instancia global
cooldown_manager = CooldownManager()
