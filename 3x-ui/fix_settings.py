import sqlite3
conn = sqlite3.connect("bot_database.db")

# Restore the original values that our test run overwrote
restores = {
    "welcome_text": "\u0628\u0647 NigVpn \u062e\u0648\u0634 \u0622\u0645\u062f\u06cc\u062f! \u062e\u0631\u06cc\u062f \u0622\u0633\u0627\u0646 \u0648 \u0627\u0645\u0646 VPN",
    "currency_symbol": "\u062a\u0648\u0645\u0627\u0646",
    "currency": "IRR",
}
for key, val in restores.items():
    conn.execute("UPDATE settings SET value = ? WHERE key = ?", (val, key))
    print(f"Restored {key}")

conn.commit()
conn.close()
print("Done")
