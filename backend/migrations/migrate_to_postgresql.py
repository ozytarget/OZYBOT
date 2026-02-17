"""
PostgreSQL Migration Script
Migrates SQLite database to PostgreSQL for production reliability
"""
import sqlite3
import os

def generate_postgresql_schema():
    """
    Genera el schema SQL completo para PostgreSQL
    """
    schema = """
-- PostgreSQL Schema for Trading Bot
-- Production-ready with proper data types and constraints

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bot configuration
CREATE TABLE IF NOT EXISTS bot_config (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    demo_mode BOOLEAN DEFAULT TRUE,
    auto_close_enabled BOOLEAN DEFAULT FALSE,
    stop_loss_percent DECIMAL(5,2) DEFAULT 2.0,
    take_profit_percent DECIMAL(5,2) DEFAULT 5.0,
    UNIQUE(user_id)
);

-- Positions (main trading table)
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('buy', 'sell')),
    quantity DECIMAL(18,8) NOT NULL,
    entry_price DECIMAL(18,8) NOT NULL,
    current_price DECIMAL(18,8),
    exit_price DECIMAL(18,8),
    pnl DECIMAL(18,2) DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    
    -- Risk Management
    highest_price DECIMAL(18,8),
    trailing_stop DECIMAL(18,8),
    break_even_active BOOLEAN DEFAULT FALSE,
    tp1_closed BOOLEAN DEFAULT FALSE,
    tp2_closed BOOLEAN DEFAULT FALSE,
    remaining_quantity DECIMAL(18,8),
    close_reason TEXT,
    alert_price DECIMAL(18,8),
    
    -- Timestamps
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading statistics
CREATE TABLE IF NOT EXISTS trading_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_profit DECIMAL(18,2) DEFAULT 0.0,
    
    -- Advanced metrics
    max_drawdown DECIMAL(18,2) DEFAULT 0.0,
    current_drawdown DECIMAL(18,2) DEFAULT 0.0,
    avg_profit DECIMAL(18,2) DEFAULT 0.0,
    avg_loss DECIMAL(18,2) DEFAULT 0.0,
    largest_win DECIMAL(18,2) DEFAULT 0.0,
    largest_loss DECIMAL(18,2) DEFAULT 0.0,
    consecutive_wins INTEGER DEFAULT 0,
    consecutive_losses INTEGER DEFAULT 0,
    
    UNIQUE(user_id)
);

-- Partial closes
CREATE TABLE IF NOT EXISTS partial_closes (
    id SERIAL PRIMARY KEY,
    position_id INTEGER NOT NULL REFERENCES positions(id) ON DELETE CASCADE,
    quantity DECIMAL(18,8) NOT NULL,
    price DECIMAL(18,8) NOT NULL,
    reason VARCHAR(50),
    closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trade logs (forensic)
CREATE TABLE IF NOT EXISTS trade_logs (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    price DECIMAL(18,8),
    quantity DECIMAL(18,8),
    reason TEXT,
    slippage DECIMAL(10,4),
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Connection status
CREATE TABLE IF NOT EXISTS connection_status (
    id INTEGER PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    last_update TIMESTAMP NOT NULL,
    latency_ms INTEGER
);

-- Equity curve
CREATE TABLE IF NOT EXISTS equity_curve (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    snapshot_time TIMESTAMP NOT NULL,
    total_balance DECIMAL(18,2) NOT NULL,
    realized_profit DECIMAL(18,2) DEFAULT 0.0
);

-- PROFESSIONAL SAFETY TABLES

-- Ticker cooldowns (Anti-Whipsaw)
CREATE TABLE IF NOT EXISTS ticker_cooldowns (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    activated_at TIMESTAMP NOT NULL,
    cooldown_until TIMESTAMP NOT NULL,
    reason TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(ticker, activated_at)
);

-- Slippage records
CREATE TABLE IF NOT EXISTS slippage_records (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id) ON DELETE CASCADE,
    ticker VARCHAR(20) NOT NULL,
    expected_price DECIMAL(18,8) NOT NULL,
    actual_price DECIMAL(18,8) NOT NULL,
    slippage_dollars DECIMAL(18,8),
    slippage_percent DECIMAL(10,4),
    is_acceptable BOOLEAN DEFAULT TRUE,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System health (Heartbeat)
CREATE TABLE IF NOT EXISTS system_health (
    id INTEGER PRIMARY KEY,
    service VARCHAR(100) NOT NULL,
    last_heartbeat TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'alive',
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    last_error_at TIMESTAMP
);

-- Panic events (Kill Switch)
CREATE TABLE IF NOT EXISTS panic_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    positions_closed INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE
);

-- System logs (Advanced logging)
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    service VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Broker connections
CREATE TABLE IF NOT EXISTS broker_connections (
    id SERIAL PRIMARY KEY,
    broker VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    last_check TIMESTAMP NOT NULL,
    latency_ms INTEGER,
    error_message TEXT,
    consecutive_failures INTEGER DEFAULT 0
);

-- INDICES for performance

CREATE INDEX idx_positions_user_status ON positions(user_id, status);
CREATE INDEX idx_positions_symbol ON positions(symbol);
CREATE INDEX idx_trade_logs_position ON trade_logs(position_id, created_at);
CREATE INDEX idx_ticker_cooldowns_active ON ticker_cooldowns(ticker, is_active);
CREATE INDEX idx_slippage_ticker ON slippage_records(ticker, recorded_at);
CREATE INDEX idx_system_logs_level ON system_logs(level, created_at DESC);
CREATE INDEX idx_equity_curve_user_time ON equity_curve(user_id, snapshot_time DESC);

-- TRIGGERS for updated_at

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_positions_updated_at
    BEFORE UPDATE ON positions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Default admin user (password: admin123 - CAMBIAR EN PRODUCCIÓN)
INSERT INTO users (username, email, password_hash) 
VALUES ('admin', 'admin@tradingbot.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5kdZQXoSKOCgu')
ON CONFLICT (username) DO NOTHING;
"""
    
    return schema

def export_data_to_sql():
    """
    Exporta datos de SQLite a SQL statements para PostgreSQL
    """
    try:
        conn = sqlite3.connect('trading_bot.db')
        cursor = conn.cursor()
        
        # Obtener todos los datos
        tables = ['users', 'bot_config', 'positions', 'trading_stats']
        
        sql_statements = []
        
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if rows:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                for row in rows:
                    values = ', '.join([f"'{val}'" if val is not None else 'NULL' for val in row])
                    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({values});"
                    sql_statements.append(sql)
        
        conn.close()
        
        return '\n'.join(sql_statements)
        
    except Exception as e:
        print(f"❌ Error exportando datos: {str(e)}")
        return None

def save_migration_files():
    """
    Guarda los archivos de migración a PostgreSQL
    """
    # Schema
    schema = generate_postgresql_schema()
    with open('postgresql_schema.sql', 'w') as f:
        f.write(schema)
    print("✅ Archivo generado: postgresql_schema.sql")
    
    # Data export
    data_sql = export_data_to_sql()
    if data_sql:
        with open('postgresql_data.sql', 'w') as f:
            f.write(data_sql)
        print("✅ Archivo generado: postgresql_data.sql")
    
    # Railway config
    railway_config = """
# Railway PostgreSQL Setup

## 1. Crear PostgreSQL database en Railway:
railway add
# Selecciona: PostgreSQL

## 2. Obtener connection string:
railway variables
# Copia DATABASE_URL

## 3. Conectar a PostgreSQL:
psql $DATABASE_URL

## 4. Ejecutar schema:
\\i postgresql_schema.sql

## 5. Importar datos (opcional):
\\i postgresql_data.sql

## 6. Actualizar backend/config.py:
```python
import os
DATABASE_URL = os.getenv('DATABASE_URL')
# Cambiar de sqlite3 a psycopg2
```

## 7. Actualizar requirements.txt:
psycopg2-binary==2.9.9

## 8. Redesplegar:
git push origin main
"""
    
    with open('POSTGRESQL_MIGRATION.md', 'w') as f:
        f.write(railway_config)
    print("✅ Archivo generado: POSTGRESQL_MIGRATION.md")

if __name__ == '__main__':
    print("🐘 Generando migración a PostgreSQL...")
    save_migration_files()
    print("\n✅ Migración lista. Lee POSTGRESQL_MIGRATION.md para instrucciones.")
