"""
Slippage Tracker Service
Compara precio esperado (TradingView) vs precio real de ejecución
"""
import sqlite3
from datetime import datetime

class SlippageTracker:
    def __init__(self, db_path='trading_bot.db'):
        self.db_path = db_path
        self.max_acceptable_slippage = 0.001  # 0.1% por defecto
    
    def record_slippage(self, position_id, expected_price, actual_price, ticker):
        """
        Registra el slippage de una orden
        
        Args:
            position_id: ID de la posición
            expected_price: Precio que envió TradingView
            actual_price: Precio real de ejecución
            ticker: Symbol del activo
        
        Returns:
            dict: {
                'slippage_percent': float,
                'slippage_dollars': float,
                'acceptable': bool,
                'warning': str or None
            }
        """
        try:
            # Calcular slippage
            slippage_dollars = actual_price - expected_price
            slippage_percent = (slippage_dollars / expected_price) * 100 if expected_price > 0 else 0
            
            # Determinar si es aceptable
            is_acceptable = abs(slippage_percent) <= (self.max_acceptable_slippage * 100)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Guardar en base de datos
            cursor.execute("""
                INSERT INTO slippage_records
                (position_id, ticker, expected_price, actual_price, 
                 slippage_dollars, slippage_percent, is_acceptable, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (position_id, ticker, expected_price, actual_price,
                  slippage_dollars, slippage_percent, is_acceptable, 
                  datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            # Generar warning si slippage es alto
            warning = None
            if not is_acceptable:
                warning = f"⚠️ SLIPPAGE ALTO: {ticker} | Esperado: ${expected_price:.2f} | Real: ${actual_price:.2f} | Dif: {slippage_percent:.3f}%"
                print(warning)
            
            return {
                'success': True,
                'slippage_percent': slippage_percent,
                'slippage_dollars': slippage_dollars,
                'acceptable': is_acceptable,
                'warning': warning
            }
            
        except Exception as e:
            print(f"❌ Error registrando slippage: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_slippage_stats(self, ticker=None, days=7):
        """
        Obtiene estadísticas de slippage
        
        Args:
            ticker: Filtrar por ticker específico (opcional)
            days: Últimos N días
        
        Returns:
            dict: Estadísticas de slippage
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if ticker:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_trades,
                        AVG(slippage_percent) as avg_slippage,
                        MAX(slippage_percent) as max_slippage,
                        MIN(slippage_percent) as min_slippage,
                        SUM(CASE WHEN is_acceptable = 0 THEN 1 ELSE 0 END) as high_slippage_count
                    FROM slippage_records
                    WHERE ticker = ? 
                    AND recorded_at >= datetime('now', '-' || ? || ' days')
                """, (ticker, days))
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_trades,
                        AVG(slippage_percent) as avg_slippage,
                        MAX(slippage_percent) as max_slippage,
                        MIN(slippage_percent) as min_slippage,
                        SUM(CASE WHEN is_acceptable = 0 THEN 1 ELSE 0 END) as high_slippage_count
                    FROM slippage_records
                    WHERE recorded_at >= datetime('now', '-' || ? || ' days')
                """, (days,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result or result[0] == 0:
                return {
                    'success': True,
                    'total_trades': 0,
                    'avg_slippage': 0,
                    'max_slippage': 0,
                    'min_slippage': 0,
                    'high_slippage_count': 0,
                    'high_slippage_rate': 0
                }
            
            total, avg, max_slip, min_slip, high_count = result
            
            return {
                'success': True,
                'total_trades': total,
                'avg_slippage': round(avg, 4) if avg else 0,
                'max_slippage': round(max_slip, 4) if max_slip else 0,
                'min_slippage': round(min_slip, 4) if min_slip else 0,
                'high_slippage_count': high_count,
                'high_slippage_rate': round((high_count / total) * 100, 2) if total > 0 else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_recent_slippage_events(self, limit=20):
        """
        Obtiene los últimos eventos de slippage registrados
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    ticker, expected_price, actual_price,
                    slippage_dollars, slippage_percent, is_acceptable, recorded_at
                FROM slippage_records
                ORDER BY recorded_at DESC
                LIMIT ?
            """, (limit,))
            
            events = cursor.fetchall()
            conn.close()
            
            return {
                'success': True,
                'events': [
                    {
                        'ticker': row[0],
                        'expected_price': row[1],
                        'actual_price': row[2],
                        'slippage_dollars': row[3],
                        'slippage_percent': row[4],
                        'acceptable': bool(row[5]),
                        'timestamp': row[6]
                    }
                    for row in events
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_broker_quality(self, ticker, threshold_percent=5.0):
        """
        Analiza si el broker tiene problemas con un ticker específico
        
        Returns:
            dict: {
                'ticker': str,
                'quality_score': float (0-100),
                'recommendation': str,
                'avg_slippage': float
            }
        """
        stats = self.get_slippage_stats(ticker=ticker, days=7)
        
        if not stats['success'] or stats['total_trades'] == 0:
            return {
                'ticker': ticker,
                'quality_score': None,
                'recommendation': 'Insufficient data',
                'avg_slippage': 0
            }
        
        # Calcular score de calidad (100 = perfecto, 0 = terrible)
        high_slippage_rate = stats['high_slippage_rate']
        avg_slippage = abs(stats['avg_slippage'])
        
        quality_score = max(0, 100 - (high_slippage_rate * 10) - (avg_slippage * 500))
        
        # Generar recomendación
        if quality_score >= 80:
            recommendation = '✅ Excelente - Continuar operando'
        elif quality_score >= 60:
            recommendation = '⚠️ Aceptable - Monitorear de cerca'
        elif quality_score >= 40:
            recommendation = '❌ Pobre - Considerar cambiar broker o timeframe'
        else:
            recommendation = '🚫 CRÍTICO - NO operar este ticker con este broker'
        
        return {
            'ticker': ticker,
            'quality_score': round(quality_score, 2),
            'recommendation': recommendation,
            'avg_slippage': stats['avg_slippage'],
            'high_slippage_rate': stats['high_slippage_rate'],
            'total_trades': stats['total_trades']
        }


# Instancia global
slippage_tracker = SlippageTracker()
