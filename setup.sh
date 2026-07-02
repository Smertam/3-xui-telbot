#!/bin/bash
set -e

REPO="https://github.com/Smertam/3-xui-telbot.git"
INSTALL_DIR="/root/robot"

echo "=== Installing robot... ==="

# Install system dependencies
apt update -qq
apt install -y -qq python3 python3-venv python3-pip >/dev/null 2>&1

# Clone or pull
if [ -d "$INSTALL_DIR/.git" ]; then
    cd "$INSTALL_DIR"
    git pull
else
    rm -rf "$INSTALL_DIR"
    git clone "$REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Setup venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q

# Create .env if missing
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo ">>> Edit .env with your credentials:"
    echo "    nano $INSTALL_DIR/.env"
    echo ""
fi

# Kill old process
kill -9 $(lsof -ti:5000) 2>/dev/null || true

# Start bot
nohup ./venv/bin/python run.py > bot.log 2>&1 &
sleep 2

if lsof -ti:5000 >/dev/null 2>&1; then
    echo "=== Robot is running on port 5000 ==="
else
    echo "=== Failed to start. Check: tail -50 $INSTALL_DIR/bot.log ==="
fi
