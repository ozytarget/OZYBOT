"""
WebSocket Service para precios en tiempo real
Conecta con Binance, Alpaca, o Twelve Data
"""
import json
import sqlite3
import time
from threading import Thread
from datetime import datetime

# Import asyncio and websockets with error handling
try:
    import asyncio
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ websockets no disponible: {str(e)}")
    WEBSOCKETS_AVAILABLE = False
    asyncio = None

class RealTimePriceService:
    def __init__(self, db_path='trading_bot.db'):
        self.db_path = db_path
        self.connections = {}
        self.last_prices = {}
        self.running = False
        self.thread = None
        
    def get_active_tickers(self):
        """Obtiene los tickers con posiciones abiertas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT ticker FROM positions WHERE status = 'open'
            """)
            
            tickers = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return tickers
        except Exception as e:
            print(f"❌ Error obteniendo tickers: {str(e)}")
            return []
    
    def map_ticker_to_binance(self, ticker):
        """Mapea ticker a formato Binance"""
        ticker_map = {
            'BTCUSD': 'btcusdt',
            'ETHUSD': 'ethusdt',
            'BNBUSD': 'bnbusdt',
            'ADAUSD': 'adausdt',
            'SOLUSD': 'solusdt',
            'XRPUSD': 'xrpusdt',
            'DOGEUSD': 'dogeusdt'
        }
        
        return ticker_map.get(ticker, ticker.lower().replace('USD', 'usdt'))
    
    async def connect_binance_websocket(self, ticker):
        """Conecta al WebSocket de Binance para un ticker"""
        binance_ticker = self.map_ticker_to_binance(ticker)
        uri = f"wss://stream.binance.com:9443/ws/{binance_ticker}@trade"
        
        try:
            async with websockets.connect(uri) as websocket:
                print(f"🔌 Conectado a Binance WebSocket: {binance_ticker}")
                self.update_connection_status('Binance', 'connected', 0)
                
                while self.running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=10)
                        data = json.loads(message)
                        
                        # Extraer precio del mensaje
                        price = float(data.get('p', 0))
                        
                        if price > 0:
                            # Guardar última precio y color
                            old_price = self.last_prices.get(ticker, price)
                            color = 'green' if price > old_price else 'red' if price < old_price else 'gray'
                            
                            self.last_prices[ticker] = {
                                'price': price,
                                'color': color,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # Actualizar en base de datos
                            self.update_position_prices(ticker, price)
                            
                    except asyncio.TimeoutError:
                        # Enviar ping para mantener conexión
                        await websocket.ping()
                    except Exception as e:
                        print(f"⚠️ Error en WebSocket {ticker}: {str(e)}")
                        self.update_connection_status('Binance', 'error', 0)
                        break
                        
        except Exception as e:
            print(f"❌ Error conectando a Binance {ticker}: {str(e)}")
            self.update_connection_status('Binance', 'disconnected', 0)
    
    def update_position_prices(self, ticker, price):
        """Actualiza precios de posiciones en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Actualizar posiciones abiertas con este ticker
            cursor.execute("""
                UPDATE positions 
                SET current_price = ?,
                    updated_at = ?
                WHERE ticker = ? AND status = 'open'
            """, (price, datetime.now().isoformat(), ticker))
            
            # Obtener posiciones afectadas para calcular PnL
            cursor.execute("""
                SELECT id, entry_price, quantity, side, remaining_quantity
                FROM positions 
                WHERE ticker = ? AND status = 'open'
            """, (ticker,))
            
            positions = cursor.fetchall()
            
            for pos in positions:
                pos_id, entry_price, quantity, side, remaining_qty = pos
                
                # Usar remaining_quantity si existe
                qty = remaining_qty if remaining_qty else quantity
                
                # Calcular PnL
                if side == 'buy':
                    pnl = (price - entry_price) * qty
                else:
                    pnl = (entry_price - price) * qty
                
                cursor.execute("""
                    UPDATE positions 
                    SET pnl = ?
                    WHERE id = ?
                """, (pnl, pos_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error actualizando precios: {str(e)}")
    
    def update_connection_status(self, source, status, latency_ms):
        """Actualiza el status de conexión para el LED indicator"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO connection_status 
                (id, source, status, last_update, latency_ms)
                VALUES (1, ?, ?, ?, ?)
            """, (source, status, datetime.now().isoformat(), latency_ms))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error actualizando connection status: {str(e)}")
    
    async def run_websocket_loop(self):
        """Loop principal de WebSockets"""
        while self.running:
            tickers = self.get_active_tickers()
            
            if not tickers:
                print("⏸️ No hay posiciones abiertas, esperando...")
                await asyncio.sleep(10)
                continue
            
            # Crear tareas para cada ticker
            tasks = [self.connect_binance_websocket(ticker) for ticker in tickers]
            
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                print(f"❌ Error en websocket loop: {str(e)}")
                await asyncio.sleep(5)
    
    def start(self):
        """Inicia el servicio de WebSocket en thread separado"""
        if not WEBSOCKETS_AVAILABLE:
            print("⚠️ WebSocket Service deshabilitado - websockets no disponible")
            return
            
        if self.running:
            print("⚠️ WebSocket Service ya está corriendo")
            return
        
        self.running = True
        
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_websocket_loop())
        
        self.thread = Thread(target=run_async_loop, daemon=True)
        self.thread.start()
        print("✅ WebSocket Service iniciado")
    
    def stop(self):
        """Detiene el servicio"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        print("✅ WebSocket Service detenido")
    
    def get_last_prices(self):
        """Retorna los últimos precios con colores"""
        return self.last_prices


# Instancia global
realtime_price_service = RealTimePriceService()
