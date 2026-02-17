import sqlite3

conn = sqlite3.connect('trading.db')
cursor = conn.cursor()

cursor.execute('SELECT id, symbol, side, quantity, entry_price, status FROM positions')
positions = cursor.fetchall()

print(f'\n✅ Total posiciones: {len(positions)}\n')
for p in positions:
    print(f'  #{p[0]}: {p[1]} {p[2]} {p[3]} @ ${p[4]} [{p[5]}]')

cursor.execute('SELECT COUNT(*) FROM webhooks')
wh_count = cursor.fetchone()[0]
print(f'\nWebhooks recibidos: {wh_count}')

conn.close()
