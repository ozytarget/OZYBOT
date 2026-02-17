"""
Migration: Add demo_mode column to bot_config table
"""
import sqlite3
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def run_migration():
    """Add demo_mode column to bot_config if it doesn't exist"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(bot_config)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'demo_mode' not in columns:
            print("Adding demo_mode column to bot_config...")
            cursor.execute('''
                ALTER TABLE bot_config 
                ADD COLUMN demo_mode BOOLEAN DEFAULT 1
            ''')
            conn.commit()
            print("✅ Migration completed: demo_mode column added")
        else:
            print("ℹ️ Column demo_mode already exists, skipping migration")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    run_migration()
