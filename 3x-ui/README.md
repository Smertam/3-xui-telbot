# 3x-ui Telegram Bot

A complete Python Telegram bot using aiogram that integrates with 3x-ui panel for selling VPN configs with a wallet-based payment system.

## Features

### User Features
- **Wallet System**: Top up balance via manual receipt upload
- **Free Test**: One free test config (24h validity)
- **Buy Configs**: Purchase monthly subscription configs
- **My Configs**: View and manage active configs
- **QR Codes**: Subscription links with QR codes

### Admin Features
- **Receipt Management**: Approve/reject payment receipts
- **User Management**: Search, view, ban/unban users
- **Statistics**: View total users, configs, revenue
- **Settings**: Edit welcome text, config price, duration
- **Multi-Admin**: Add/remove admin users

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=your_telegram_id

PANEL_URL=https://your-panel-domain.com
PANEL_USER=admin
PANEL_PASS=your_panel_password

CONFIG_PRICE=5.00
FREE_TEST_DAYS=1
CONFIG_MONTHS=1
```

### 3. Run the Bot
```bash
python bot.py
```

## Project Structure

```
3x-ui-bot/
├── bot.py              # Main entry point
├── config.py           # Configuration
├── database.py         # Database operations
├── api.py              # 3x-ui API integration
├── handlers/
│   ├── user.py         # User commands
│   ├── wallet.py       # Wallet operations
│   ├── admin.py        # Admin panel
│   └── callback.py     # Callback handlers
├── keyboards/
│   ├── user.py         # User keyboards
│   └── admin.py        # Admin keyboards
├── utils/
│   ├── qr_generator.py # QR code generation
│   └── texts.py        # Message templates
├── middlewares/
│   └── __init__.py     # Auth middleware
├── requirements.txt
├── .env.example
└── README.md
```

## Bot Commands

### User Commands
- `/start` - Welcome message and registration
- `/menu` - Main menu

### Admin Commands
- `/admin` - Admin panel

## 3x-ui Panel Requirements

The bot expects a 3x-ui panel with:
- VLESS protocol inbound configured
- API access enabled
- Valid admin credentials

## License

MIT
