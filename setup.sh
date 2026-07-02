#!/bin/bash
set -e

REPO="https://github.com/Smertam/3-xui-telbot.git"
INSTALL_DIR="/root/robot"

echo ""
echo "========================================="
echo "       Robot Installer"
echo "========================================="
echo ""

# Install system dependencies
echo "[1/6] Installing system dependencies..."
apt update -qq
apt install -y -qq python3 python3-venv python3-pip >/dev/null 2>&1

# Clone or pull
echo "[2/6] Downloading files..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd "$INSTALL_DIR"
    git pull -q
else
    rm -rf "$INSTALL_DIR"
    git clone "$REPO" "$INSTALL_DIR" -q
    cd "$INSTALL_DIR"
fi

# Setup venv
echo "[3/6] Installing Python packages..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q

# Interactive .env setup
echo "[4/6] Configuring..."
echo ""
echo "--- Bot Settings ---"
read -p "Bot Token (from @BotFather): " BOT_TOKEN
read -p "Admin Telegram IDs (comma separated, e.g. 123456,789012): " ADMIN_IDS
read -p "Notification Channel ID (leave empty to skip): " CHANNEL_ID

echo ""
echo "--- Panel Settings ---"
read -p "Panel URL (e.g. https://example.com:5443/something): " PANEL_URL
read -p "Panel Username: " PANEL_USER
read -p "Panel Password: " PANEL_PASS

echo ""
echo "--- Config Defaults ---"
read -p "Config Price (default 5): " CONFIG_PRICE
CONFIG_PRICE=${CONFIG_PRICE:-5}
read -p "Free Test Days (default 1): " FREE_TEST_DAYS
FREE_TEST_DAYS=${FREE_TEST_DAYS:-1}
read -p "Config Duration in Months (default 1): " CONFIG_MONTHS
CONFIG_MONTHS=${CONFIG_MONTHS:-1}

echo ""
echo "--- Web Admin Panel ---"
read -p "Web Panel Username (default admin): " ADMIN_WEB_USER
ADMIN_WEB_USER=${ADMIN_WEB_USER:-admin}
read -p "Web Panel Password (default admin): " ADMIN_WEB_PASS
ADMIN_WEB_PASS=${ADMIN_WEB_PASS:-admin}
read -p "Web Panel Port (default 5000): " WEB_PORT
WEB_PORT=${WEB_PORT:-5000}
SECRET_KEY=$(openssl rand -hex 16 2>/dev/null || head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n' | head -c 32)

# Write .env
cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_IDS=$ADMIN_IDS
CHANNEL_ID=$CHANNEL_ID

PANEL_URL=$PANEL_URL
PANEL_USER=$PANEL_USER
PANEL_PASS=$PANEL_PASS

CONFIG_PRICE=$CONFIG_PRICE
FREE_TEST_DAYS=$FREE_TEST_DAYS
CONFIG_MONTHS=$CONFIG_MONTHS

DB_PATH=bot_database.db

ADMIN_WEB_USER=$ADMIN_WEB_USER
ADMIN_WEB_PASS=$ADMIN_WEB_PASS
SECRET_KEY=$SECRET_KEY
WEB_PORT=$WEB_PORT
EOF

echo ""
echo "[5/6] Starting robot..."

# Kill old process
kill -9 $(lsof -ti:$WEB_PORT) 2>/dev/null || true

# Start bot
nohup ./venv/bin/python run.py > bot.log 2>&1 &
sleep 3

echo "[6/6] Done!"
echo ""
if lsof -ti:$WEB_PORT >/dev/null 2>&1; then
    echo "========================================="
    echo "  Robot is running!"
    echo "  Web Panel: http://YOUR_IP:$WEB_PORT"
    echo "  Login: $ADMIN_WEB_USER / $ADMIN_WEB_PASS"
    echo "========================================="
else
    echo "========================================="
    echo "  Something went wrong."
    echo "  Check: tail -50 $INSTALL_DIR/bot.log"
    echo "========================================="
fi
