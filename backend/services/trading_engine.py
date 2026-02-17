"""
Professional Trading Engine
Gestión avanzada de riesgo, trailing stops, break-even, cierres parciales
"""
import sqlite3
from datetime import datetime
from typing import Dict, Optional, Tuple
import json

class TradingEngine:
    def __init__(self, db_path='trading_bot.db'):
        self.db_path = db_path
        self.slippage_threshold = 0.001  # 0.1% máximo slippage permitido
        
    def get_connection(self):
        """Obtiene conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def calculate_pnl(self, entry_price: float, current_price: float, 
                     quantity: float, side: str) -> Tuple[float, float]:
        """
        Calcula P&L realizado y porcentaje
        Returns: (pnl_dollars, pnl_percent)
        """
        if side == 'buy':
            pnl_dollars = (current_price - entry_price) * quantity
        else:  # sell/short
            pnl_dollars = (entry_price - current_price) * quantity
        
        cost_basis = entry_price * quantity
        pnl_percent = (pnl_dollars / cost_basis) * 100 if cost_basis > 0 else 0
        
        return pnl_dollars, pnl_percent
    
    def check_slippage(self, alert_price: float, execution_price: float) -> bool:
        """
        Verifica si el slippage es aceptable
        Returns: True si es aceptable, False si excede threshold
        """
        if alert_price == 0:
            return True
        
        slippage = abs(execution_price - alert_price) / alert_price
        return slippage <= self.slippage_threshold
    
    def calculate_trailing_stop(self, entry_price: float, current_price: float,
                                highest_price: float, side: str, 
                                trailing_percent: float = 1.0) -> float:
        """
        Calcula el precio del Trailing Stop Loss
        Si el precio sube 1%, el SL sube proporcionalmente
        """
        if side == 'buy':
            # Para posiciones long
            if highest_price > entry_price:
                # SL se mueve hacia arriba siguiendo el precio
                trailing_stop = highest_price * (1 - trailing_percent / 100)
                return max(trailing_stop, entry_price * 0.98)  # Mínimo 2% debajo del entry
            else:
                # Si no ha subido, usar stop loss inicial
                return entry_price * 0.98
        else:  # sell/short
            # Para posiciones short (inverso)
            if highest_price < entry_price:
                trailing_stop = highest_price * (1 + trailing_percent / 100)
                return min(trailing_stop, entry_price * 1.02)
            else:
                return entry_price * 1.02
    
    def should_break_even(self, pnl_percent: float, current_stop: float,
                         entry_price: float, commission: float = 0.001) -> Optional[float]:
        """
        Verifica si debe activar Break-Even Protection
        Al alcanzar +1.5%, mueve SL a entry_price + comisión
        Returns: nuevo stop price si debe activarse, None si no
        """
        if pnl_percent >= 1.5:
            # Mover stop a break-even (Entry + comisión)
            break_even_price = entry_price * (1 + commission)
            if current_stop < break_even_price:
                return break_even_price
        return None
    
    def calculate_partial_closes(self, entry_price: float, current_price: float,
                                 quantity: float, side: str) -> Dict:
        """
        Calcula cierres parciales:
        - TP1: 50% de la posición al +2%
        - TP2: 50% restante al +5%
        Returns: dict con información de cierres parciales
        """
        _, pnl_percent = self.calculate_pnl(entry_price, current_price, quantity, side)
        
        result = {
            'tp1_triggered': False,
            'tp2_triggered': False,
            'tp1_quantity': 0,
            'tp2_quantity': 0,
            'tp1_price': 0,
            'tp2_price': 0
        }
        
        if side == 'buy':
            result['tp1_price'] = entry_price * 1.02  # +2%
            result['tp2_price'] = entry_price * 1.05  # +5%
        else:  # short
            result['tp1_price'] = entry_price * 0.98  # -2%
            result['tp2_price'] = entry_price * 0.95  # -5%
        
        # TP1: Cierra 50% al alcanzar 2%
        if pnl_percent >= 2.0:
            result['tp1_triggered'] = True
            result['tp1_quantity'] = quantity * 0.5
        
        # TP2: Cierra el resto al alcanzar 5%
        if pnl_percent >= 5.0:
            result['tp2_triggered'] = True
            result['tp2_quantity'] = quantity * 0.5
        
        return result
    
    def update_position_risk_management(self, position_id: int, current_price: float):
        """
        Actualiza una posición con toda la lógica de risk management avanzado
        - Trailing Stop Loss
        - Break-Even Protection
        - Cierres Parciales
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener posición actual
            cursor.execute("""
                SELECT entry_price, current_price, quantity, side, 
                       highest_price, trailing_stop, break_even_active,
                       tp1_closed, tp2_closed, remaining_quantity
                FROM positions 
                WHERE id = ? AND status = 'open'
            """, (position_id,))
            
            position = cursor.fetchone()
            if not position:
                return
            
            (entry_price, old_current_price, original_quantity, side,
             highest_price, trailing_stop, break_even_active,
             tp1_closed, tp2_closed, remaining_quantity) = position
            
            # Si no hay remaining_quantity, usar original
            if remaining_quantity is None:
                remaining_quantity = original_quantity
            
            # Actualizar highest_price (para trailing stop)
            if side == 'buy':
                new_highest = max(highest_price or entry_price, current_price)
            else:
                new_highest = min(highest_price or entry_price, current_price)
            
            # Calcular P&L actual
            pnl_dollars, pnl_percent = self.calculate_pnl(
                entry_price, current_price, remaining_quantity, side
            )
            
            # 1. TRAILING STOP LOSS
            new_trailing_stop = self.calculate_trailing_stop(
                entry_price, current_price, new_highest, side, trailing_percent=1.0
            )
            
            # 2. BREAK-EVEN PROTECTION
            new_break_even = None
            if not break_even_active:
                new_break_even = self.should_break_even(
                    pnl_percent, new_trailing_stop, entry_price
                )
                if new_break_even:
                    new_trailing_stop = new_break_even
                    break_even_active = True
                    print(f"🛡️ Break-Even activado para posición {position_id} @ ${new_break_even:.2f}")
            
            # 3. CIERRES PARCIALES
            partials = self.calculate_partial_closes(
                entry_price, current_price, original_quantity, side
            )
            
            # Ejecutar TP1 si no se ha cerrado
            if partials['tp1_triggered'] and not tp1_closed:
                self.execute_partial_close(
                    position_id, partials['tp1_quantity'], 
                    partials['tp1_price'], "TP1", cursor
                )
                remaining_quantity -= partials['tp1_quantity']
                tp1_closed = True
                print(f"💰 TP1 ejecutado: {partials['tp1_quantity']} @ ${partials['tp1_price']:.2f}")
            
            # Ejecutar TP2 si no se ha cerrado
            if partials['tp2_triggered'] and not tp2_closed:
                self.execute_partial_close(
                    position_id, partials['tp2_quantity'],
                    partials['tp2_price'], "TP2", cursor
                )
                remaining_quantity -= partials['tp2_quantity']
                tp2_closed = True
                print(f"💰 TP2 ejecutado: {partials['tp2_quantity']} @ ${partials['tp2_price']:.2f}")
            
            # 4. CHECK TRAILING STOP - CIERRE TOTAL
            stop_hit = False
            if side == 'buy' and current_price <= new_trailing_stop:
                stop_hit = True
            elif side == 'sell' and current_price >= new_trailing_stop:
                stop_hit = True
            
            if stop_hit:
                self.close_position_by_trailing_stop(
                    position_id, current_price, pnl_dollars, cursor
                )
                print(f"🔴 Trailing Stop ejecutado @ ${current_price:.2f} | P&L: ${pnl_dollars:.2f}")
            else:
                # Actualizar posición con nuevos valores
                cursor.execute("""
                    UPDATE positions 
                    SET current_price = ?,
                        pnl = ?,
                        highest_price = ?,
                        trailing_stop = ?,
                        break_even_active = ?,
                        tp1_closed = ?,
                        tp2_closed = ?,
                        remaining_quantity = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (current_price, pnl_dollars, new_highest, new_trailing_stop,
                      break_even_active, tp1_closed, tp2_closed, remaining_quantity,
                      datetime.now().isoformat(), position_id))
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Error en risk management: {str(e)}")
            conn.rollback()
        finally:
            conn.close()
    
    def execute_partial_close(self, position_id: int, quantity: float,
                              price: float, reason: str, cursor):
        """Ejecuta un cierre parcial y registra en logs"""
        # Registrar en tabla de partial_closes
        cursor.execute("""
            INSERT INTO partial_closes 
            (position_id, quantity, price, reason, closed_at)
            VALUES (?, ?, ?, ?, ?)
        """, (position_id, quantity, price, reason, datetime.now().isoformat()))
        
        # Calcular P&L del cierre parcial
        cursor.execute("""
            SELECT entry_price, side FROM positions WHERE id = ?
        """, (position_id,))
        entry_price, side = cursor.fetchone()
        
        partial_pnl, _ = self.calculate_pnl(entry_price, price, quantity, side)
        
        # Actualizar trading_stats
        cursor.execute("""
            UPDATE trading_stats 
            SET total_profit = total_profit + ?
            WHERE user_id = (SELECT user_id FROM positions WHERE id = ?)
        """, (partial_pnl, position_id))
    
    def close_position_by_trailing_stop(self, position_id: int, 
                                       exit_price: float, pnl: float, cursor):
        """Cierra una posición completamente por trailing stop"""
        cursor.execute("""
            UPDATE positions 
            SET status = 'closed',
                exit_price = ?,
                pnl = ?,
                close_reason = 'Trailing Stop',
                closed_at = ?
            WHERE id = ?
        """, (exit_price, pnl, datetime.now().isoformat(), position_id))
        
        # Actualizar estadísticas
        if pnl > 0:
            cursor.execute("""
                UPDATE trading_stats 
                SET winning_trades = winning_trades + 1,
                    total_profit = total_profit + ?
                WHERE user_id = (SELECT user_id FROM positions WHERE id = ?)
            """, (pnl, position_id))
        else:
            cursor.execute("""
                UPDATE trading_stats 
                SET losing_trades = losing_trades + 1,
                    total_profit = total_profit + ?
                WHERE user_id = (SELECT user_id FROM positions WHERE id = ?)
            """, (pnl, position_id))
    
    def log_trade_forensics(self, position_id: int, entry_reason: str,
                           slippage: float, duration_seconds: int):
        """
        Guarda logs forenses detallados de cada trade
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trade_logs 
            (position_id, entry_reason, slippage, duration_seconds, logged_at)
            VALUES (?, ?, ?, ?, ?)
        """, (position_id, entry_reason, slippage, duration_seconds, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()


# Instancia global
trading_engine = TradingEngine()
