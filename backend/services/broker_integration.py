"""
Broker Integration Service
Conecta con APIs reales: Alpaca, Binance, Interactive Brokers
"""
import os
import requests
from datetime import datetime

class BrokerService:
    def __init__(self, broker='alpaca'):
        self.broker = broker
        
        # Alpaca Configuration
        if broker == 'alpaca':
            self.api_key = os.getenv('ALPACA_API_KEY')
            self.api_secret = os.getenv('ALPACA_API_SECRET')
            self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
            self.headers = {
                'APCA-API-KEY-ID': self.api_key,
                'APCA-API-SECRET-KEY': self.api_secret
            }
        
        # Binance Configuration
        elif broker == 'binance':
            self.api_key = os.getenv('BINANCE_API_KEY')
            self.api_secret = os.getenv('BINANCE_API_SECRET')
            self.base_url = 'https://api.binance.com'
    
    def place_order_real(self, symbol, side, quantity, order_type='market'):
        """
        Ejecuta orden REAL en el broker
        
        IMPORTANTE: Esto usa dinero real si no estás en paper trading
        """
        if self.broker == 'alpaca':
            return self._alpaca_place_order(symbol, side, quantity, order_type)
        elif self.broker == 'binance':
            return self._binance_place_order(symbol, side, quantity, order_type)
    
    def _alpaca_place_order(self, symbol, side, quantity, order_type):
        """Alpaca Market Order"""
        try:
            url = f"{self.base_url}/v2/orders"
            data = {
                "symbol": symbol,
                "qty": quantity,
                "side": side,  # 'buy' or 'sell'
                "type": order_type,
                "time_in_force": "gtc"
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 200:
                order = response.json()
                return {
                    'success': True,
                    'order_id': order['id'],
                    'filled_price': order.get('filled_avg_price'),
                    'status': order['status'],
                    'timestamp': order['created_at']
                }
            else:
                return {
                    'success': False,
                    'error': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _binance_place_order(self, symbol, side, quantity, order_type):
        """Binance Market Order"""
        # Implementar Binance API
        # Requiere firma HMAC-SHA256
        pass
    
    def get_account_balance(self):
        """Obtiene el balance real de la cuenta"""
        if self.broker == 'alpaca':
            try:
                url = f"{self.base_url}/v2/account"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    account = response.json()
                    return {
                        'success': True,
                        'cash': float(account['cash']),
                        'portfolio_value': float(account['portfolio_value']),
                        'buying_power': float(account['buying_power'])
                    }
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def get_positions_real(self):
        """Obtiene posiciones reales del broker"""
        if self.broker == 'alpaca':
            try:
                url = f"{self.base_url}/v2/positions"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    positions = response.json()
                    return {
                        'success': True,
                        'positions': positions
                    }
            except Exception as e:
                return {'success': False, 'error': str(e)}


# Instancia global
broker_service = BrokerService(broker='alpaca')
