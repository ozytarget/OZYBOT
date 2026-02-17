"""
Sistema de Notificaciones para Telegram y Discord
Envía alertas cuando se abren/cierran operaciones
"""
import json
import os
from datetime import datetime

# Import requests with error handling
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ requests no disponible - notificaciones deshabilitadas: {str(e)}")
    REQUESTS_AVAILABLE = False

class NotificationService:
    def __init__(self):
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
        
    def send_telegram_message(self, message):
        """Envía mensaje a Telegram"""
        if not REQUESTS_AVAILABLE:
            print("⚠️ requests not available - cannot send Telegram notification")
            return False
            
        if not self.telegram_bot_token or not self.telegram_chat_id:
            print("⚠️ Telegram credentials not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            params = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=params, timeout=10)
            
            if response.status_code == 200:
                print("✅ Telegram notification sent")
                return True
            else:
                print(f"❌ Telegram error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Telegram: {str(e)}")
            return False
    
    def send_discord_message(self, message, color=None):
        """Envía mensaje a Discord"""
        if not REQUESTS_AVAILABLE:
            print("⚠️ requests not available - cannot send Discord notification")
            return False
            
        if not self.discord_webhook_url:
            print("⚠️ Discord webhook not configured")
            return False
        
        try:
            # Formato embed para Discord
            embed = {
                "title": "🤖 Trading Bot Alert",
                "description": message,
                "color": color or 3447003,  # azul por defecto
                "timestamp": datetime.now().isoformat()
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                print("✅ Discord notification sent")
                return True
            else:
                print(f"❌ Discord error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Discord: {str(e)}")
            return False
    
    def notify_position_opened(self, ticker, side, quantity, entry_price, balance):
        """Notifica cuando se abre una posición"""
        message = f"""
🟢 <b>POSITION OPENED</b>

📊 Ticker: {ticker}
📈 Side: {side.upper()}
💰 Quantity: {quantity}
💵 Entry Price: ${entry_price:.2f}
📍 Total Value: ${entry_price * quantity:.2f}
💼 Remaining Balance: ${balance:.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Enviar a Telegram
        self.send_telegram_message(message)
        
        # Enviar a Discord (verde)
        discord_msg = message.replace('<b>', '**').replace('</b>', '**')
        self.send_discord_message(discord_msg, color=3066993)  # verde
    
    def notify_position_closed(self, ticker, side, quantity, entry_price, 
                              exit_price, pnl, pnl_percent, balance, reason="Manual"):
        """Notifica cuando se cierra una posición"""
        
        # Determinar emoji según P&L
        emoji = "🟢" if pnl >= 0 else "🔴"
        profit_label = "PROFIT" if pnl >= 0 else "LOSS"
        
        message = f"""
{emoji} <b>POSITION CLOSED - {profit_label}</b>

📊 Ticker: {ticker}
📈 Side: {side.upper()}
💰 Quantity: {quantity}

💵 Entry: ${entry_price:.2f}
💵 Exit: ${exit_price:.2f}

📊 P&L: ${pnl:+.2f} ({pnl_percent:+.2f}%)
📍 Close Reason: {reason}
💼 New Balance: ${balance:.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Enviar a Telegram
        self.send_telegram_message(message)
        
        # Enviar a Discord
        discord_msg = message.replace('<b>', '**').replace('</b>', '**')
        color = 3066993 if pnl >= 0 else 15158332  # verde o rojo
        self.send_discord_message(discord_msg, color=color)
    
    def notify_partial_close(self, ticker, quantity, price, reason, pnl, remaining_qty):
        """Notifica un cierre parcial (TP1, TP2)"""
        message = f"""
💰 <b>PARTIAL CLOSE - {reason}</b>

📊 Ticker: {ticker}
💰 Quantity Closed: {quantity}
💵 Price: ${price:.2f}
📊 Partial P&L: ${pnl:+.2f}
📍 Remaining: {remaining_qty} units

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.send_telegram_message(message)
        
        discord_msg = message.replace('<b>', '**').replace('</b>', '**')
        self.send_discord_message(discord_msg, color=16776960)  # amarillo
    
    def notify_break_even_activated(self, ticker, break_even_price):
        """Notifica cuando se activa Break-Even Protection"""
        message = f"""
🛡️ <b>BREAK-EVEN ACTIVATED</b>

📊 Ticker: {ticker}
💵 Stop Loss moved to: ${break_even_price:.2f}
✅ Risk: ZERO (Entry + Commission)

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.send_telegram_message(message)
        
        discord_msg = message.replace('<b>', '**').replace('</b>', '**')
        self.send_discord_message(discord_msg, color=3447003)  # azul


# Instancia global
notification_service = NotificationService()
