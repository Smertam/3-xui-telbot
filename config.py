import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

PANEL_URL = os.getenv("PANEL_URL", "")
PANEL_USER = os.getenv("PANEL_USER", "")
PANEL_PASS = os.getenv("PANEL_PASS", "")

CONFIG_PRICE = float(os.getenv("CONFIG_PRICE", "5.00"))
FREE_TEST_DAYS = int(os.getenv("FREE_TEST_DAYS", "1"))
CONFIG_MONTHS = int(os.getenv("CONFIG_MONTHS", "1"))

DB_PATH = os.getenv("DB_PATH", "bot_database.db")
