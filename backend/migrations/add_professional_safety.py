"""
Migration: Add Professional Safety Tables
Creates tables for: panic mode, heartbeat, cooldowns, slippage, system health
"""
import sqlite3
from datetime import datetime

def run_migration():
    """Creates all professional safety tables"""
    try:
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        print("🔧 Ejecutando migración: Professional Safety Features...")
        
        # 1. TICKER COOLDOWNS (Anti-Whipsaw)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticker_cooldowns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                activated_at TIMESTAMP NOT NULL,
                cooldown_until TIMESTAMP NOT NULL,
                reason TEXT,
                is_active BOOLEAN DEFAULT 1,
                UNIQUE(ticker, activated_at)
            )
        ''')
        print("✅ Tabla ticker_cooldowns creada")
        
        # 2. SLIPPAGE RECORDS (Backtest vs Forward)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS slippage_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id INTEGER,
                ticker TEXT NOT NULL,
                expected_price REAL NOT NULL,
                actual_price REAL NOT NULL,
                slippage_dollars REAL,
                slippage_percent REAL,
                is_acceptable BOOLEAN DEFAULT 1,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (position_id) REFERENCES positions(id)
            )
        ''')
        print("✅ Tabla slippage_records creada")
        
        # 3. SYSTEM HEALTH (Heartbeat Monitor)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_health (
                id INTEGER PRIMARY KEY,
                service TEXT NOT NULL,
                last_heartbeat TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'alive',
                error_count INTEGER DEFAULT 0,
                last_error TEXT,
                last_error_at TIMESTAMP
            )
        ''')
        print("✅ Tabla system_health creada")
        
        # 4. PANIC HISTORY (Kill Switch Events)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS panic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                positions_closed INTEGER DEFAULT 0,
                success BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("✅ Tabla panic_events creada")
        
        # 5. ADVANCED LOGS (System-level logging)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                service TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla system_logs creada")
        
        # 6. BROKER CONNECTION STATUS (Enhanced monitoring)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broker_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                broker TEXT NOT NULL,
                status TEXT NOT NULL,
                last_check TIMESTAMP NOT NULL,
                latency_ms INTEGER,
                error_message TEXT,
                consecutive_failures INTEGER DEFAULT 0
            )
        ''')
        print("✅ Tabla broker_connections creada")
        
        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_cooldowns_active ON ticker_cooldowns(ticker, is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_slippage_ticker ON slippage_records(ticker, recorded_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level, created_at)')
        print("✅ Índices creados")
        
        conn.commit()
        conn.close()
        
        print("✅ Migración 'Professional Safety Features' completada exitosamente")
        return {'success': True}
        
    except Exception as e:
        print(f"❌ Error en migración Professional Safety Features: {str(e)}")
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    run_migration()
