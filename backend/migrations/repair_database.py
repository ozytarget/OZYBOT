"""
Database Repair Script: Ensures all users have required config entries
Run this manually if users are missing bot_config, trading_stats, or broker_settings
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def repair_database():
    """Ensure all users have bot_config, trading_stats, and broker_settings"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Get all users
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users in database")
        
        for user_row in users:
            user_id = user_row[0]
            repaired = []
            
            # Check and create bot_config
            cursor.execute("SELECT id FROM bot_config WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO bot_config (user_id, is_active, demo_mode) 
                    VALUES (?, 0, 1)
                ''', (user_id,))
                repaired.append("bot_config")
            
            # Check and create trading_stats
            cursor.execute("SELECT id FROM trading_stats WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO trading_stats (user_id) VALUES (?)', (user_id,))
                repaired.append("trading_stats")
            
            # Check and create broker_settings
            cursor.execute("SELECT id FROM broker_settings WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO broker_settings (user_id) VALUES (?)', (user_id,))
                repaired.append("broker_settings")
            
            if repaired:
                print(f"✅ Repaired user {user_id}: created {', '.join(repaired)}")
        
        conn.commit()
        print("\n✅ Database repair completed successfully")
        
    except Exception as e:
        print(f"❌ Repair failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    repair_database()
