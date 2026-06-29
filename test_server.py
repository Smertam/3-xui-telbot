import sys, os
sys.path.insert(0, "/root/3x-ui")
os.chdir("/root/3x-ui")
try:
    from utils.texts import BOT_TEXTS
    print(f"Loaded {len(BOT_TEXTS)} texts")
    import asyncio
    from utils.texts import wallet_text
    result = asyncio.run(wallet_text(100000))
    print(result[:200])
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
