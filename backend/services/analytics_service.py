"""
Advanced Analytics Service
Calcula Win Rate, Drawdown, Average Profit/Loss, Equity Curve
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class AnalyticsService:
    def __init__(self, db_path='trading_bot.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def calculate_win_rate(self, user_id: int) -> Dict:
        """Calcula Win Rate y estadísticas relacionadas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener todas las operaciones cerradas
        cursor.execute("""
            SELECT pnl FROM positions 
            WHERE user_id = ? AND status = 'closed' AND pnl IS NOT NULL
        """, (user_id,))
        
        trades = cursor.fetchall()
        conn.close()
        
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_profit': 0.0,
                'avg_loss': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'profit_factor': 0.0
            }
        
        pnls = [trade[0] for trade in trades]
        
        winning_trades = [pnl for pnl in pnls if pnl > 0]
        losing_trades = [pnl for pnl in pnls if pnl < 0]
        
        total_trades = len(pnls)
        num_wins = len(winning_trades)
        num_losses = len(losing_trades)
        
        win_rate = (num_wins / total_trades * 100) if total_trades > 0 else 0
        
        avg_profit = sum(winning_trades) / num_wins if num_wins > 0 else 0
        avg_loss = sum(losing_trades) / num_losses if num_losses > 0 else 0
        
        largest_win = max(winning_trades) if winning_trades else 0
        largest_loss = min(losing_trades) if losing_trades else 0
        
        total_profit = sum(winning_trades)
        total_loss = abs(sum(losing_trades))
        
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': num_wins,
            'losing_trades': num_losses,
            'win_rate': round(win_rate, 2),
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'largest_win': round(largest_win, 2),
            'largest_loss': round(largest_loss, 2),
            'profit_factor': round(profit_factor, 2)
        }
    
    def calculate_drawdown(self, user_id: int) -> Dict:
        """
        Calcula Maximum Drawdown y Current Drawdown
        Drawdown = caída desde el peak más alto
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener equity curve
        cursor.execute("""
            SELECT equity, timestamp 
            FROM equity_curve 
            WHERE user_id = ?
            ORDER BY timestamp ASC
        """, (user_id,))
        
        equity_data = cursor.fetchall()
        conn.close()
        
        if not equity_data:
            return {
                'max_drawdown': 0.0,
                'max_drawdown_percent': 0.0,
                'current_drawdown': 0.0,
                'current_drawdown_percent': 0.0
            }
        
        equities = [row[0] for row in equity_data]
        
        peak = equities[0]
        max_dd = 0
        current_dd = 0
        
        for equity in equities:
            if equity > peak:
                peak = equity
            
            dd = peak - equity
            
            if dd > max_dd:
                max_dd = dd
            
            current_dd = dd
        
        max_dd_percent = (max_dd / peak * 100) if peak > 0 else 0
        current_dd_percent = (current_dd / peak * 100) if peak > 0 else 0
        
        return {
            'max_drawdown': round(max_dd, 2),
            'max_drawdown_percent': round(max_dd_percent, 2),
            'current_drawdown': round(current_dd, 2),
            'current_drawdown_percent': round(current_dd_percent, 2)
        }
    
    def get_equity_curve(self, user_id: int, period_hours: int = 24) -> List[Dict]:
        """Obtiene la equity curve de las últimas X horas para el gráfico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calcular timestamp de inicio
        start_time = (datetime.now() - timedelta(hours=period_hours)).isoformat()
        
        cursor.execute("""
            SELECT equity, timestamp 
            FROM equity_curve 
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """, (user_id, start_time))
        
        data = cursor.fetchall()
        conn.close()
        
        return [
            {'equity': row[0], 'timestamp': row[1]}
            for row in data
        ]
    
    def update_equity_snapshot(self, user_id: int, current_equity: float):
        """Guarda un snapshot del equity actual para la curva"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO equity_curve (user_id, equity, timestamp)
            VALUES (?, ?, ?)
        """, (user_id, current_equity, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_consecutive_wins_losses(self, user_id: int) -> Dict:
        """Calcula rachas actuales de victorias/derrotas consecutivas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pnl FROM positions 
            WHERE user_id = ? AND status = 'closed' AND pnl IS NOT NULL
            ORDER BY closed_at DESC
        """, (user_id,))
        
        trades = cursor.fetchall()
        conn.close()
        
        if not trades:
            return {'consecutive_wins': 0, 'consecutive_losses': 0}
        
        # Contar racha actual
        consecutive_wins = 0
        consecutive_losses = 0
        
        for trade in trades:
            pnl = trade[0]
            
            if pnl > 0:
                consecutive_wins += 1
                break
            elif pnl < 0:
                consecutive_losses += 1
                break
        
        # Si la primera fue ganancia, seguir contando
        if consecutive_wins > 0:
            for trade in trades[1:]:
                if trade[0] > 0:
                    consecutive_wins += 1
                else:
                    break
        
        # Si la primera fue pérdida, seguir contando
        if consecutive_losses > 0:
            for trade in trades[1:]:
                if trade[0] < 0:
                    consecutive_losses += 1
                else:
                    break
        
        return {
            'consecutive_wins': consecutive_wins,
            'consecutive_losses': consecutive_losses
        }
    
    def get_full_analytics(self, user_id: int) -> Dict:
        """Obtiene todas las estadísticas de analytics en un solo call"""
        win_rate_stats = self.calculate_win_rate(user_id)
        drawdown_stats = self.calculate_drawdown(user_id)
        streak_stats = self.get_consecutive_wins_losses(user_id)
        equity_curve = self.get_equity_curve(user_id, period_hours=24)
        
        return {
            **win_rate_stats,
            **drawdown_stats,
            **streak_stats,
            'equity_curve': equity_curve
        }
    
    def update_trading_stats(self, user_id: int):
        """Actualiza la tabla trading_stats con los analytics calculados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        analytics = self.get_full_analytics(user_id)
        
        cursor.execute("""
            UPDATE trading_stats 
            SET max_drawdown = ?,
                avg_profit = ?,
                avg_loss = ?,
                largest_win = ?,
                largest_loss = ?,
                consecutive_wins = ?,
                consecutive_losses = ?
            WHERE user_id = ?
        """, (
            analytics['max_drawdown'],
            analytics['avg_profit'],
            analytics['avg_loss'],
            analytics['largest_win'],
            analytics['largest_loss'],
            analytics['consecutive_wins'],
            analytics['consecutive_losses'],
            user_id
        ))
        
        conn.commit()
        conn.close()


# Instancia global
analytics_service = AnalyticsService()
