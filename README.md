# 3X-UI Telegram Bot / ربات تلگرامی 3X-UI

A Telegram bot for selling VPN configs (VLESS/VMess) connected to a 3x-ui panel. Includes a web admin panel for managing users, plans, configs, and settings.

ربات تلگرامی برای فروش کانفیگ VPN (VLESS/VMess) متصل به پنل 3x-ui. دارای پنل مدیریت وب برای مدیریت کاربران، پلن‌ها، کانفیگ‌ها و تنظیمات.

---

## Features / قابلیت‌ها

- Buy VPN config (card-to-card & wallet payment)
- Free test config
- My Services (QR code, sub link, volume info, change link)
- Buy extra volume
- Admin panel (users, plans, receipts, stats, settings)
- Button customization (emoji & style)
- Menu layout editor
- Bot text customization
- Force join channel
- New user & receipt notifications

- خرید کانفیگ VPN (کارت به کارت و کیف پول)
- کانفیگ رایگان تست
- سرویس‌های من (کد QR، لینک اشتراک، اطلاعات حجم، تغییر لینک)
- خرید حجم اضافه
- پنل مدیریت (کاربران، پلن‌ها، رسیدها، آمار، تنظیمات)
- سفارشی‌سازی دکمه‌ها (ایموجی و استایل)
- ویرایشگر لایوت منو
- سفارشی‌سازی متن‌های ربات
- اجبار به عضویت در کانال
- اعلان کاربر جدید و رسید

---

## One-Command Install / نصب با یک دستور

Run this on your server (Ubuntu/Debian):

این دستور را روی سرور خود اجرا کنید (Ubuntu/Debian):

```bash
bash <(curl -s https://raw.githubusercontent.com/Smertam/3-xui-telbot/master/setup.sh)
```

The installer will ask you for:

نصب‌کننده از شما می‌پرسد:

| Field | توضیح |
|-------|-------|
| Bot Token | From @BotFather / از @BotFather |
| Admin IDs | Your Telegram user ID / آیدی تلگرام شما |
| Channel ID | Notification channel (optional) / کانال اعلان (اختیاری) |
| Panel URL | 3x-ui panel URL / آدرس پنل 3x-ui |
| Panel User | Panel username / نام کاربری پنل |
| Panel Pass | Panel password / رمز پنل |
| Config Price | Default price / قیمت پیش‌فرض |
| Free Test Days | Trial duration / مدت تست رایگان |
| Config Months | Config duration / مدت اعتبار کانفیگ |
| Web Panel User | Admin panel login / نام کاربری پنل مدیریت |
| Web Panel Pass | Admin panel password / رمز پنل مدیریت |
| Web Panel Port | Default 5000 / پیش‌فرض 5000 |

---

## Manual Install / نصب دستی

```bash
git clone https://github.com/Smertam/3-xui-telbot.git /root/robot
cd /root/robot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Fill in your credentials
nohup ./venv/bin/python run.py > bot.log 2>&1 &
```

git clone https://github.com/Smertam/3-xui-telbot.git /root/robot
cd /root/robot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # اطلاعات خود را وارد کنید
nohup ./venv/bin/python run.py > bot.log 2>&1 &

---

## Update / بروزرسانی

```bash
cd /root/robot
git pull
source venv/bin/activate
pip install -r requirements.txt
kill -9 $(lsof -ti:5000)
nohup ./venv/bin/python run.py > bot.log 2>&1 &
```

---

## Web Panel / پنل مدیریت

Access at `http://YOUR_IP:5000`

دسترسی از `http://YOUR_IP:5000`

Manage: users, plans, configs, receipts, settings, bot texts, button styles, menu layout.

مدیریت: کاربران، پلن‌ها، کانفیگ‌ها، رسیدها، تنظیمات، متن‌های ربات، استایل دکمه‌ها، لایوت منو.

---

## Tech Stack / تکنولوژی‌ها

- Python 3 + aiogram 3
- Flask (web admin panel)
- SQLite (bot_database.db)
- 3x-ui / Xray panel API

---

## License / لایسنس

MIT
