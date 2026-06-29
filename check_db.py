import sqlite3
conn = sqlite3.connect('/root/3x-ui/bot_database.db')
conn.row_factory = sqlite3.Row
for key in ['panel_url','panel_user','panel_pass','inbound_id','sub_link_template']:
    row = conn.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()
    val = row['value'] if row else 'NOT SET'
    print(f'{key} = {val}')
conn.close()
