"""
Price Monitor Service
Actualiza automáticamente los precios de activos y recalcula PnL
"""
import yfinance as yf
import sqlite3
import time
from threading import Thread
from datetime import datetime

class PriceMonitor:
    def __init__(self, db_path='trading_bot.db', update_interval=5):
        self.db_path = db_path
        self.update_interval = update_interval  # seconds
        self.running = False
        self.thread = None
        
        # Mapeo de tickers TradingView a Yahoo Finance
        self.ticker_map = {
            'BTCUSD': 'BTC-USD',
            'ETHUSD': 'ETH-USD',
            'XAUUSD': 'GC=F',  # Gold futures
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'USDJPY': 'JPY=X',
            'SPX': '^GSPC',
            'NDX': '^NDX',
            'DJI': '^DJI',
            # Stocks usan el mismo ticker
        }
    
    def map_ticker(self, ticker):
        """Convierte ticker de TradingView a Yahoo Finance"""
        # Si está en el mapeo, usar el mapeo
        if ticker in self.ticker_map:
            return self.ticker_map[ticker]
        # Si no, asumir que es un stock normal
        return ticker
    
    def get_current_price(self, ticker):
        """Obtiene el precio actual de un ticker usando yfinance"""
        try:
            yf_ticker = self.map_ticker(ticker)
            stock = yf.Ticker(yf_ticker)
            
            # Intentar obtener precio actual
            info = stock.info
            
            # Probar diferentes campos en orden de preferencia
            price = (
                info.get('regularMarketPrice') or 
                info.get('currentPrice') or
                info.get('previousClose')
            )
            
            if price:
                return float(price)
            
            # Si no hay precio en info, intentar con history
            hist = stock.history(period='1d', interval='1m')
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            
            return None
        except Exception as e:
            print(f"⚠️ Error obteniendo precio para {ticker}: {str(e)}")
            return None
    
    def update_positions_prices(self):
        """Actualiza los precios de todas las posiciones abiertas y recalcula PnL"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener todas las posiciones abiertas
            cursor.execute("""
                SELECT id, ticker, side, quantity, entry_price 
                FROM positions 
                WHERE status = 'open'
            """)
            
            positions = cursor.fetchall()
            
            if not positions:
                conn.close()
                return
            
            print(f"🔄 Actualizando {len(positions)} posiciones...")
            
            for position in positions:
                pos_id, ticker, side, quantity, entry_price = position
                
                # Obtener precio actual
                current_price = self.get_current_price(ticker)
                
                if current_price is None:
                    print(f"⚠️ No se pudo obtener precio para {ticker}")
                    continue
                
                # Calcular PnL
                if side == 'buy':
                    pnl = (current_price - entry_price) * quantity
                else:  # sell/short
                    pnl = (entry_price - current_price) * quantity
                
                # Actualizar posición
                cursor.execute("""
                    UPDATE positions 
                    SET current_price = ?, pnl = ?, updated_at = ?
                    WHERE id = ?
                """, (current_price, pnl, datetime.now().isoformat(), pos_id))
                
                print(f"✅ {ticker}: ${entry_price:.2f} -> ${current_price:.2f} | PnL: ${pnl:.2f}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error actualizando precios: {str(e)}")
    
    def check_stop_loss_take_profit(self):
        """Verifica si alguna posición alcanzó SL/TP y cierra automáticamente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener configuración de auto_close
            cursor.execute("""
                SELECT auto_close_enabled, stop_loss_percent, take_profit_percent
                FROM bot_config
                LIMIT 1
            """)
            
            config = cursor.fetchone()
            if not config or not config[0]:  # auto_close_enabled = False
                conn.close()
                return
            
            auto_close_enabled, stop_loss_percent, take_profit_percent = config
            
            # Obtener posiciones abiertas con PnL calculado
            cursor.execute("""
                SELECT id, ticker, entry_price, current_price, pnl, quantity
                FROM positions 
                WHERE status = 'open' AND current_price IS NOT NULL
            """)
            
            positions = cursor.fetchall()
            
            for position in positions:
                pos_id, ticker, entry_price, current_price, pnl, quantity = position
                
                # Calcular porcentaje de ganancia/pérdida
                pnl_percent = (pnl / (entry_price * quantity)) * 100
                
                should_close = False
                close_reason = ""
                
                # Check Stop Loss
                if pnl_percent <= -stop_loss_percent:
                    should_close = True
                    close_reason = f"Stop Loss ({pnl_percent:.2f}%)"
                
                # Check Take Profit
                elif pnl_percent >= take_profit_percent:
                    should_close = True
                    close_reason = f"Take Profit ({pnl_percent:.2f}%)"
                
                if should_close:
                    # Cerrar posición
                    cursor.execute("""
                        UPDATE positions 
                        SET status = 'closed', exit_price = ?, closed_at = ?
                        WHERE id = ?
                    """, (current_price, datetime.now().isoformat(), pos_id))
                    
                    # Actualizar estadísticas
                    if pnl > 0:
                        cursor.execute("""
                            UPDATE trading_stats 
                            SET winning_trades = winning_trades + 1,
                                total_profit = total_profit + ?
                            WHERE user_id = (SELECT user_id FROM positions WHERE id = ?)
                        """, (pnl, pos_id))
                    else:
                        cursor.execute("""
                            UPDATE trading_stats 
                            SET losing_trades = losing_trades + 1,
                                total_profit = total_profit + ?
                            WHERE user_id = (SELECT user_id FROM positions WHERE id = ?)
                        """, (pnl, pos_id))
                    
                    print(f"🔴 Posición cerrada automáticamente: {ticker} | {close_reason} | PnL: ${pnl:.2f}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error verificando SL/TP: {str(e)}")
    
    def monitor_loop(self):
        """Loop principal de monitoreo"""
        print(f"🚀 Price Monitor iniciado (actualización cada {self.update_interval}s)")
        
        while self.running:
            try:
                self.update_positions_prices()
                self.check_stop_loss_take_profit()
            except Exception as e:
                print(f"❌ Error en monitor loop: {str(e)}")
            
            time.sleep(self.update_interval)
        
        print("⛔ Price Monitor detenido")
    
    def start(self):
        """Inicia el monitor en un thread separado"""
        if self.running:
            print("⚠️ Price Monitor ya está corriendo")
            return
        
        self.running = True
        self.thread = Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
        print("✅ Price Monitor iniciado")
    
    def stop(self):
        """Detiene el monitor"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        print("✅ Price Monitor detenido")


# Instancia global del monitor
price_monitor = PriceMonitor(update_interval=5)  # Actualiza cada 5 segundos
