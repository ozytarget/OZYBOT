"""
Migración: Añade campos para risk management avanzado
"""
import sqlite3

def run_migration():
    """Añade columnas para trailing stops, break-even, y cierres parciales"""
    conn = sqlite3.connect('trading_bot.db')
    cursor = conn.cursor()
    
    try:
        # Añadir columnas a positions
        new_columns = [
            "highest_price REAL DEFAULT 0",
            "trailing_stop REAL DEFAULT 0",
            "break_even_active BOOLEAN DEFAULT 0",
            "tp1_closed BOOLEAN DEFAULT 0",
            "tp2_closed BOOLEAN DEFAULT 0",
            "remaining_quantity REAL",
            "close_reason TEXT",
            "alert_price REAL DEFAULT 0"
        ]
        
        for column in new_columns:
            try:
                cursor.execute(f"ALTER TABLE positions ADD COLUMN {column}")
                print(f"✅ Añadida columna: {column.split()[0]}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"⚠️ Columna ya existe: {column.split()[0]}")
                else:
                    raise
        
        # Crear tabla de partial_closes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partial_closes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                reason TEXT,
                closed_at TEXT NOT NULL,
                FOREIGN KEY (position_id) REFERENCES positions (id)
            )
        """)
        print("✅ Tabla partial_closes creada")
        
        # Crear tabla de trade_logs (logs forenses)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id INTEGER NOT NULL,
                entry_reason TEXT,
                slippage REAL,
                duration_seconds INTEGER,
                logged_at TEXT NOT NULL,
                FOREIGN KEY (position_id) REFERENCES positions (id)
            )
        """)
        print("✅ Tabla trade_logs creada")
        
        # Crear tabla de conexión status (para LED indicator)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                last_update TEXT NOT NULL,
                latency_ms INTEGER DEFAULT 0
            )
        """)
        print("✅ Tabla connection_status creada")
        
        # Añadir columnas a trading_stats para analytics avanzados
        analytics_columns = [
            "max_drawdown REAL DEFAULT 0",
            "current_drawdown REAL DEFAULT 0",
            "avg_profit REAL DEFAULT 0",
            "avg_loss REAL DEFAULT 0",
            "largest_win REAL DEFAULT 0",
            "largest_loss REAL DEFAULT 0",
            "consecutive_wins INTEGER DEFAULT 0",
            "consecutive_losses INTEGER DEFAULT 0"
        ]
        
        for column in analytics_columns:
            try:
                cursor.execute(f"ALTER TABLE trading_stats ADD COLUMN {column}")
                print(f"✅ Añadida columna analytics: {column.split()[0]}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"⚠️ Columna ya existe: {column.split()[0]}")
                else:
                    raise
        
        # Crear tabla de equity_curve (para el gráfico)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equity_curve (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                equity REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("✅ Tabla equity_curve creada")
        
        # Inicializar remaining_quantity para posiciones existentes
        cursor.execute("""
            UPDATE positions 
            SET remaining_quantity = quantity 
            WHERE remaining_quantity IS NULL AND status = 'open'
        """)
        
        conn.commit()
        print("✅ Migración de risk management completada")
        
    except Exception as e:
        print(f"❌ Error en migración: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    run_migration()
