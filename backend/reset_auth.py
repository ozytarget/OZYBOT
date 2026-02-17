"""
Script para resetear y ver usuarios en la base de datos
"""
import sqlite3
from auth_utils import hash_password
from config import Config

def list_users():
    """Lista todos los usuarios en la base de datos"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, email, created_at FROM users')
        users = cursor.fetchall()
        
        if users:
            print("\n📋 USUARIOS EN LA BASE DE DATOS:")
            print("-" * 60)
            for user in users:
                print(f"ID: {user['id']} | Email: {user['email']} | Creado: {user['created_at']}")
            print("-" * 60)
            print(f"Total: {len(users)} usuario(s)")
        else:
            print("\n❌ No hay usuarios en la base de datos")
        
        conn.close()
        return len(users)
    except Exception as e:
        print(f"❌ Error listando usuarios: {str(e)}")
        return 0

def delete_user(email):
    """Elimina un usuario por email"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get user_id first
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Usuario '{email}' no encontrado")
            conn.close()
            return False
        
        user_id = user[0]
        
        # Delete related data
        cursor.execute('DELETE FROM bot_config WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM broker_settings WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM trading_stats WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM positions WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Usuario '{email}' eliminado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error eliminando usuario: {str(e)}")
        return False

def create_user(email, password):
    """Crea un nuevo usuario"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            print(f"❌ Usuario '{email}' ya existe")
            conn.close()
            return False
        
        # Create user
        password_hash = hash_password(password)
        cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)',
                      (email, password_hash))
        user_id = cursor.lastrowid
        
        # Initialize bot config
        cursor.execute('INSERT INTO bot_config (user_id) VALUES (?)', (user_id,))
        
        # Initialize broker settings
        cursor.execute('INSERT INTO broker_settings (user_id) VALUES (?)', (user_id,))
        
        # Initialize trading stats
        cursor.execute('INSERT INTO trading_stats (user_id) VALUES (?)', (user_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Usuario '{email}' creado exitosamente")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        return True
    except Exception as e:
        print(f"❌ Error creando usuario: {str(e)}")
        return False

def reset_all():
    """Elimina TODOS los usuarios (usar con precaución)"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM positions')
        cursor.execute('DELETE FROM trading_stats')
        cursor.execute('DELETE FROM broker_settings')
        cursor.execute('DELETE FROM bot_config')
        cursor.execute('DELETE FROM users')
        
        conn.commit()
        conn.close()
        
        print("✅ Todos los usuarios eliminados")
        return True
    except Exception as e:
        print(f"❌ Error reseteando: {str(e)}")
        return False

if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("🔧 HERRAMIENTA DE GESTIÓN DE USUARIOS")
    print("=" * 60)
    print(f"Base de datos: {Config.DATABASE_PATH}")
    print()
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python reset_auth.py list                    - Lista usuarios")
        print("  python reset_auth.py delete <email>          - Elimina usuario")
        print("  python reset_auth.py create <email> <pass>   - Crea usuario")
        print("  python reset_auth.py reset                   - Elimina TODOS")
        print()
        list_users()
    else:
        command = sys.argv[1].lower()
        
        if command == 'list':
            list_users()
        
        elif command == 'delete' and len(sys.argv) >= 3:
            email = sys.argv[2]
            if delete_user(email):
                list_users()
        
        elif command == 'create' and len(sys.argv) >= 4:
            email = sys.argv[2]
            password = sys.argv[3]
            if create_user(email, password):
                list_users()
        
        elif command == 'reset':
            confirm = input("⚠️  ¿Eliminar TODOS los usuarios? (escribe 'SI'): ")
            if confirm == 'SI':
                if reset_all():
                    list_users()
            else:
                print("❌ Cancelado")
        
        else:
            print("❌ Comando inválido")
            print("Uso: python reset_auth.py [list|delete|create|reset]")
