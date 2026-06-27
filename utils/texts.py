WELCOME_TEXT = "به NigVpn خوش آمدید! خرید آسان و امن VPN"

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.premium_emoji import pe


async def wallet_text(balance: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  💰 <b>My Wallet</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Balance: <b>{balance:,.0f} {symbol}</b>\n\n"
        f"  Upload a payment receipt to top up."
    )


async def receipt_submitted(amount: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ✅ <b>Receipt Submitted</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Amount: <b>{amount:,.0f} {symbol}</b>\n"
        f"  Status: <b>Pending Review</b>\n\n"
        f"  Admins will review your receipt."
    )


async def receipt_approved(amount: float, new_balance: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ✅ <b>Receipt Approved!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Added: <b>{amount:,.0f} {symbol}</b>\n"
        f"  New Balance: <b>{new_balance:,.0f} {symbol}</b>"
    )


async def receipt_rejected(amount: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ❌ <b>Receipt Rejected</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Amount: <b>{amount:,.0f} {symbol}</b>\n\n"
        f"  Contact admin for more info."
    )


async def config_created(sub_link: str, expire_date: str, price: int, plan_name: str, gb: int, days: int, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ✅ <b>Config Created!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  📦 Plan: <b>{plan_name}</b>\n"
        f"  📊 Volume: <b>{gb} GB</b>\n"
        f"  📅 Duration: <b>{days} days</b>\n"
        f"  💰 Price: <b>{price:,} {symbol}</b>\n"
        f"  ⏰ Expires: <b>{expire_date}</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  🔗 Sub Link:\n"
        f"<code>{sub_link}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Scan the QR code or copy the link above."
    )


async def free_test_config(sub_link: str, days: int) -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  🆓 <b>Free Test Config</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  📊 Volume: <b>100 MB</b>\n"
        f"  📅 Duration: <b>{days} day</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  🔗 Sub Link:\n"
        f"<code>{sub_link}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Scan the QR code or copy the link above.\n\n"
        f"<i>This is your free trial. Buy a full config to continue.</i>"
    )


async def no_balance(price: int, balance: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ❌ <b>Insufficient Balance</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Config Price: <b>{price:,} {symbol}</b>\n"
        f"  Your Balance: <b>{balance:,.0f} {symbol}</b>\n\n"
        f"  Top up your wallet first."
    )


async def config_list_text(configs: list[dict]) -> str:
    if not configs:
        return (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"  📋 <b>My Configs</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"  No active configs.\n"
            f"  Buy a config to get started!"
        )
    text = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  📋 <b>My Configs</b> ({len(configs)})\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    for i, cfg in enumerate(configs, 1):
        status = "🟢" if cfg["is_active"] else "🔴"
        text += f"  {status} Config #{cfg['id']} — Expires: {cfg['expire_date'][:10]}\n"
    return text


async def admin_stats(user_count: int, config_count: int, revenue: float, pending: int, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  📊 <b>Admin Stats</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  👥 Users: <b>{user_count}</b>\n"
        f"  🔑 Active Configs: <b>{config_count}</b>\n"
        f"  💰 Revenue: <b>{revenue:,.0f} {symbol}</b>\n"
        f"  📋 Pending Receipts: <b>{pending}</b>"
    )


async def receipt_info(receipt: dict, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  📋 <b>Receipt #{receipt['id']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  👤 User: @{receipt.get('username', 'N/A')} ({receipt['user_id']})\n"
        f"  💰 Amount: <b>{receipt['amount']:,.0f} {symbol}</b>\n"
        f"  📅 Date: {receipt['created_at']}\n"
        f"  📌 Status: <b>{receipt['status']}</b>"
    )


async def user_info(user: dict, symbol: str = "تومان") -> str:
    banned_text = "Yes" if user["is_banned"] else "No"
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  👤 <b>User Info</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  ID: <code>{user['id']}</code>\n"
        f"  Username: @{user.get('username', 'N/A')}\n"
        f"  Name: {user.get('first_name', 'N/A')}\n"
        f"  💰 Balance: <b>{user['balance']:,.0f} {symbol}</b>\n"
        f"  📅 Joined: {user['created_at']}\n"
        f"  🔒 Banned: {banned_text}"
    )


async def enter_amount() -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  💰 <b>Top Up Wallet</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  Enter amount (e.g., 50000):"
    )


async def setting_updated(key: str, value: str) -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ⚙️ <b>Setting Updated!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  {key}: <b>{value}</b>"
    )


async def confirm_approve(amount: float) -> str:
    return f"Approve receipt for {amount:,.0f}?"


async def confirm_reject() -> str:
    return "Reject this receipt?"


async def no_pending_receipts() -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ✅ <b>No Pending Receipts</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
