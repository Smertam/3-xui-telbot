"""
Run this script to set premium emoji IDs directly.
Usage:
  1. Send a premium emoji to @RawDataBot in Telegram
  2. It will show custom_emoji_id like: custom_emoji_id="5368324170671202286"
  3. Edit the EMOJI_MAP below with your IDs
  4. Run: python set_emojis.py
"""
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import set_setting, init_db

# EDIT THIS MAP - put your custom_emoji_id values here
# Get IDs by forwarding premium emojis to @RawDataBot
EMOJI_MAP = {
    "wallet":      "5215420556089776398",   # paste ID here
    "free_test":   "",   # paste ID here
    "buy_config":  "",   # paste ID here
    "my_configs":  "",   # paste ID here
    "back":        "",   # paste ID here
    "admin":       "",   # paste ID here
    "stats":       "",   # paste ID here
    "users":       "",   # paste ID here
    "settings":    "",   # paste ID here
    "plans":       "",   # paste ID here
    "receipts":    "",   # paste ID here
    "admins":      "",   # paste ID here
    "check":       "",   # paste ID here
    "cross":       "",   # paste ID here
    "card":        "",   # paste ID here
    "owner":       "",   # paste ID here
    "star":        "",   # paste ID here
    "copy":        "",   # paste ID here
    "cancel":      "",   # paste ID here
    "success":     "",   # paste ID here
    "approve":     "",   # paste ID here
    "reject":      "",   # paste ID here
    "ban":         "",   # paste ID here
    "unban":       "",   # paste ID here
    "plus":        "",   # paste ID here
    "minus":       "",   # paste ID here
    "list":        "",   # paste ID here
    "gear":        "",   # paste ID here
    "money":       "",   # paste ID here
    "calendar":    "",   # paste ID here
    "history":     "",   # paste ID here
    "menu":        "",   # paste ID here
    "package":     "",   # paste ID here
    "link":        "",   # paste ID here
    "clock":       "",   # paste ID here
}


async def main():
    await init_db()

    # filter out empty values
    filtered = {k: v for k, v in EMOJI_MAP.items() if v.strip()}

    if not filtered:
        print("No emoji IDs found in EMOJI_MAP.")
        print("Edit set_emojis.py and paste your custom_emoji_id values.")
        return

    await set_setting("premium_emojis", json.dumps(filtered))
    print(f"Saved {len(filtered)} premium emojis:")
    for name, eid in filtered.items():
        print(f"  {name}: {eid}")


asyncio.run(main())
