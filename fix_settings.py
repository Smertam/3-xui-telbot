import sqlite3
conn = sqlite3.connect('/root/3x-ui/bot_database.db')
settings = {
    'panel_url': 'https://212.87.199.33:16504/YYqxXzfBAVcrlmwdQw',
    'panel_user': 'elyas',
    'panel_pass': 'elyas1386z',
    'inbound_id': '1',
    'sub_link_template': '',
}
for k, v in settings.items():
    conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (k, v))
conn.commit()
for k, v in settings.items():
    row = conn.execute('SELECT value FROM settings WHERE key=?', (k,)).fetchone()
    print(f'{k} = {row[0] if row else "NOT SET"}')
conn.close()
