WELCOME_TEXT = "به NigVpn خوش آمدید! خرید آسان و امن VPN"

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.premium_emoji import pe


async def wallet_text(balance: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  💰 <b>کیف پول من</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  موجودی: <b>{balance:,.0f} {symbol}</b>\n\n"
        f"  رسید پرداخت آپلود کنید تا کیف پول شارژ شود."
    )


async def receipt_submitted(amount: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ✅ <b>رسید ارسال شد!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  مبلغ: <b>{amount:,.0f} {symbol}</b>\n"
        f"  وضعیت: <b>در انتظار بررسی</b>\n\n"
        f"  ادمین رسید شما را بررسی خواهد کرد."
    )


async def receipt_approved(amount: float, new_balance: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ✅ <b>رسید تایید شد!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  اضافه شده: <b>{amount:,.0f} {symbol}</b>\n"
        f"  موجودی جدید: <b>{new_balance:,.0f} {symbol}</b>"
    )


async def receipt_rejected(amount: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ❌ <b>رسید رد شد</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  مبلغ: <b>{amount:,.0f} {symbol}</b>\n\n"
        f"  برای اطلاعات بیشتر با ادمین تماس بگیرید."
    )


async def config_created(sub_link: str, expire_date: str, price: int, plan_name: str, gb: int, days: int, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ✅ کانفیگ ساخته شد!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  📦 پلن: {plan_name}\n"
        f"  📊 حجم: {gb} GB\n"
        f"  📅 مدت: {days} روز\n"
        f"  💰 پرداخت: {price:,} {symbol}\n"
        f"  ⏰ انقضا:{expire_date}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  🔗 لینک اشتراک:\n"
        f"<code>{sub_link}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"QR کد را اسکن کنید یا لینک بالا را کپی نمایید."
    )


async def free_test_config(sub_link: str, days: int) -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  🆓 کانفیگ تست رایگان\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  📊 حجم: 100 مگابایت\n"
        f"  📅 مدت: {days} روز\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  🔗 لینک اشتراک:\n"
        f"<code>{sub_link}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"QR کد را اسکن کنید یا لینک بالا را کپی نمایید.\n\n"
        f"<i>این تست رایگان شماست. برای ادامه، کانفیگ کامل بخرید.</i>"
    )


async def no_balance(price: int, balance: float, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ❌ <b>موجودی ناکافی</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  قیمت کانفیگ: <b>{price:,} {symbol}</b>\n"
        f"  موجودی شما: <b>{balance:,.0f} {symbol}</b>\n\n"
        f"  ابتدا کیف پول خود را شارژ کنید."
    )


async def config_list_text(configs: list[dict]) -> str:
    if not configs:
        return (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"  📋 <b>کانفیگ‌های من</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"  کانفیگ فعالی ندارید.\n"
            f"  برای شروع، کانفیگ بخرید!"
        )
    text = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  📋 <b>کانفیگ‌های من</b> ({len(configs)})\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    for i, cfg in enumerate(configs, 1):
        status = "🟢" if cfg["is_active"] else "🔴"
        text += f"  {status} کانفیگ #{cfg['id']} — انقضا: {cfg['expire_date'][:10]}\n"
    return text


async def admin_stats(user_count: int, config_count: int, revenue: float, pending: int, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  📊 <b>آمار ادمین</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  👥 کل کاربران: <b>{user_count}</b>\n"
        f"  🔑 کانفیگ‌های فعال: <b>{config_count}</b>\n"
        f"  💰 درآمد کل: <b>{revenue:,.0f} {symbol}</b>\n"
        f"  📋 رسیدهای در انتظار: <b>{pending}</b>"
    )


async def receipt_info(receipt: dict, symbol: str = "تومان") -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  📋 <b>رسید #{receipt['id']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  👤 کاربر: @{receipt.get('username', 'N/A')} ({receipt['user_id']})\n"
        f"  💰 مبلغ: <b>{receipt['amount']:,.0f} {symbol}</b>\n"
        f"  📅 تاریخ: {receipt['created_at']}\n"
        f"  📌 وضعیت: <b>{receipt['status']}</b>"
    )


async def user_info(user: dict, symbol: str = "تومان") -> str:
    banned_text = "بله" if user["is_banned"] else "خیر"
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  👤 <b>اطلاعات کاربر</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  آیدی: <code>{user['id']}</code>\n"
        f"  نام کاربری: @{user.get('username', 'N/A')}\n"
        f"  نام: {user.get('first_name', 'N/A')}\n"
        f"  💰 موجودی: <b>{user['balance']:,.0f} {symbol}</b>\n"
        f"  📅 تاریخ ثبت: {user['created_at']}\n"
        f"  🔒 مسدود: {banned_text}"
    )


async def enter_amount() -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  💰 <b>شارژ کیف پول</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  مبلغ را وارد کنید (مثال: 50000):"
    )


async def setting_updated(key: str, value: str) -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ⚙️ <b>تنظیم به‌روزرسانی شد!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  {key}: <b>{value}</b>"
    )


async def confirm_approve(amount: float) -> str:
    return f"تایید رسید به مبلغ {amount:,.0f}؟"


async def confirm_reject() -> str:
    return "رد این رسید؟"


async def no_pending_receipts() -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  ✅ <b>رسید در انتظاری وجود ندارد</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
