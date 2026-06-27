import sqlite3
conn = sqlite3.connect("bot_database.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT key, value FROM settings").fetchall()
with open("settings_dump.txt", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(f"{r['key']} = {r['value']}\n")
conn.close()
print(f"Dumped {len(rows)} settings to settings_dump.txt")
