"""
Migration: Add auto_close_enabled column to bot_config table
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def run_migration():
    """Add auto_close_enabled column to bot_config if it doesn't exist"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(bot_config)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'auto_close_enabled' not in columns:
            print("Adding auto_close_enabled column to bot_config...")
            cursor.execute('''
                ALTER TABLE bot_config 
                ADD COLUMN auto_close_enabled BOOLEAN DEFAULT 1
            ''')
            conn.commit()
            print("✅ Migration completed: auto_close_enabled column added")
        else:
            print("ℹ️ Column auto_close_enabled already exists, skipping migration")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("ℹ️ Column auto_close_enabled already exists (caught duplicate error)")
        else:
            print(f"⚠️ Migration error (non-critical): {str(e)}")
    except Exception as e:
        print(f"⚠️ Migration error (non-critical): {str(e)}")

if __name__ == '__main__':
    run_migration()
