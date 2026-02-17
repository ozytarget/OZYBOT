"""
Heartbeat Monitor Service
Detecta si el sistema está vivo y envía alertas críticas si se cae
"""
import sqlite3
import time
from datetime import datetime, timedelta
from threading import Thread
from services.notification_service import notification_service

class HeartbeatMonitor:
    def __init__(self, db_path='trading_bot.db', check_interval=30):
        self.db_path = db_path
        self.check_interval = check_interval  # segundos
        self.running = False
        self.thread = None
        self.last_heartbeat = datetime.now()
        self.alert_sent = False
    
    def update_heartbeat(self):
        """
        Actualiza el timestamp del último heartbeat
        Debe ser llamado por los servicios críticos cada X segundos
        """
        self.last_heartbeat = datetime.now()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Guardar heartbeat en DB para auditoria
            cursor.execute("""
                INSERT OR REPLACE INTO system_health 
                (id, service, last_heartbeat, status)
                VALUES (1, 'main_backend', ?, 'alive')
            """, (datetime.now().isoformat(),))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error actualizando heartbeat: {str(e)}")
    
    def check_system_health(self):
        """
        Verifica si el sistema está respondiendo correctamente
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar posiciones abiertas con riesgo
            cursor.execute("""
                SELECT COUNT(*) FROM positions WHERE status = 'open'
            """)
            open_positions = cursor.fetchone()[0]
            
            # Verificar última actualización de precios
            cursor.execute("""
                SELECT MAX(updated_at) FROM positions WHERE status = 'open'
            """)
            last_update = cursor.fetchone()[0]
            
            conn.close()
            
            # Calcular tiempo desde último update
            if last_update:
                last_update_time = datetime.fromisoformat(last_update)
                time_since_update = (datetime.now() - last_update_time).total_seconds()
            else:
                time_since_update = 0
            
            # ALERTA CRÍTICA: Posiciones abiertas pero precios sin actualizar por >60 segundos
            if open_positions > 0 and time_since_update > 60:
                return {
                    'status': 'CRITICAL',
                    'message': f'⚠️ CRÍTICO: {open_positions} posiciones abiertas pero precios sin actualizar hace {int(time_since_update)}s',
                    'open_positions': open_positions,
                    'last_update': last_update,
                    'time_since_update': time_since_update
                }
            
            # WARNING: Backend sin responder por >30 segundos
            time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
            if time_since_heartbeat > 30:
                return {
                    'status': 'WARNING',
                    'message': f'⚠️ Backend sin heartbeat hace {int(time_since_heartbeat)}s',
                    'time_since_heartbeat': time_since_heartbeat
                }
            
            return {
                'status': 'HEALTHY',
                'message': '✅ Sistema operando normalmente',
                'open_positions': open_positions,
                'last_update': last_update
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'❌ Error verificando salud del sistema: {str(e)}',
                'error': str(e)
            }
    
    def monitor_loop(self):
        """
        Loop principal del monitor (corre en background)
        """
        while self.running:
            try:
                health = self.check_system_health()
                
                # Enviar alerta si hay problemas CRÍTICOS
                if health['status'] == 'CRITICAL' and not self.alert_sent:
                    notification_service.send_critical_alert(
                        message=health['message'],
                        details=health
                    )
                    self.alert_sent = True
                    print(f"🚨 {health['message']}")
                
                # Reset flag si el sistema se recuperó
                elif health['status'] == 'HEALTHY' and self.alert_sent:
                    notification_service.send_recovery_alert(
                        message="✅ Sistema recuperado"
                    )
                    self.alert_sent = False
                    print("✅ Sistema recuperado")
                
                # Log normal
                elif health['status'] == 'HEALTHY':
                    print(f"💚 Heartbeat OK | Open positions: {health.get('open_positions', 0)}")
                
            except Exception as e:
                print(f"❌ Error en heartbeat monitor: {str(e)}")
            
            time.sleep(self.check_interval)
    
    def start(self):
        """Inicia el monitor en background thread"""
        if self.running:
            print("⚠️ Heartbeat Monitor ya está corriendo")
            return
        
        self.running = True
        self.thread = Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
        print("💚 Heartbeat Monitor iniciado")
    
    def stop(self):
        """Detiene el monitor"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("💔 Heartbeat Monitor detenido")
    
    def get_status(self):
        """
        Devuelve el status actual del monitor
        """
        health = self.check_system_health()
        return {
            'running': self.running,
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'time_since_heartbeat': (datetime.now() - self.last_heartbeat).total_seconds(),
            'health': health
        }


# Instancia global
heartbeat_monitor = HeartbeatMonitor()
