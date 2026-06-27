WELCOME_TEXT = "به NigVpn خوش آمدید! خرید آسان و امن VPN"

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.premium_emoji import pe


async def wallet_text(balance: float, symbol: str = "تومان") -> str:
    e = await pe("money")
    return (
        f"{e} <b>کیف پول شما</b>\n\n"
        f"موجودی: <b>{balance:,.0f} {symbol}</b>\n\n"
        f"با آپلود رسید پرداخت، کیف پول خود را شارژ کنید"
    )


async def receipt_submitted(amount: float, symbol: str = "تومان") -> str:
    e = await pe("check")
    return (
        f"{e} <b>رسید ارسال شد!</b>\n\n"
        f"مبلغ: <b>{amount:,.0f} {symbol}</b>\n"
        f"وضعیت: در انتظار تایید\n\n"
        f"پس از بررسی توسط ادمین، به شما اطلاع داده خواهد شد."
    )


async def receipt_approved(amount: float, new_balance: float, symbol: str = "تومان") -> str:
    e = await pe("success")
    return (
        f"{e} <b>رسید تایید شد!</b>\n\n"
        f"مبلغ اضافه شده: <b>{amount:,.0f} {symbol}</b>\n"
        f"موجودی جدید: <b>{new_balance:,.0f} {symbol}</b>"
    )


async def receipt_rejected(amount: float, symbol: str = "تومان") -> str:
    e = await pe("cross")
    return (
        f"{e} <b>رسید رد شد</b>\n\n"
        f"مبلغ: <b>{amount:,.0f} {symbol}</b>\n"
        f"برای اطلاعات بیشتر با ادمین تماس بگیرید."
    )


async def config_created(sub_link: str, expire_date: str, price: int, plan_name: str, gb: int, days: int, symbol: str = "تومان") -> str:
    e_check = await pe("success")
    e_pkg = await pe("package")
    e_money = await pe("money")
    e_link = await pe("link")
    e_cal = await pe("calendar")
    return (
        f"{e_check} <b>کانفیگ ساخته شد!</b>\n\n"
        f"{e_pkg} پلن: <b>{plan_name}</b> ({gb}GB / {days} روز)\n"
        f"{e_money} پرداخت: <b>{price:,} {symbol}</b>\n\n"
        f"{e_link} لینک اشتراک:\n`{sub_link}`\n\n"
        f"{e_cal} انقضا: {expire_date}\n\n"
        f"QR کد را اسکن کنید یا لینک بالا را کپی نمایید."
    )


async def free_test_config(sub_link: str, days: int) -> str:
    e_link = await pe("link")
    e_cal = await pe("calendar")
    return (
        f"\U0001f195 <b>کانفیگ تست رایگان</b>\n\n"
        f"{e_link} لینک اشتراک:\n`{sub_link}`\n\n"
        f"{e_cal} اعتبار: {days} روز | 100MB\n\n"
        f"QR کد را اسکن کنید یا لینک بالا را کپی نمایید.\n\n"
        f"<i>این تست رایگان شماست. برای ادامه، کانفیگ کامل بخرید.</i>"
    )


async def no_balance(price: int, balance: float, symbol: str = "تومان") -> str:
    e = await pe("cross")
    return (
        f"{e} <b>موجودی ناکافی</b>\n\n"
        f"قیمت کانفیگ: <b>{price:,} {symbol}</b>\n"
        f"موجودی شما: <b>{balance:,.0f} {symbol}</b>\n\n"
        f"ابتدا کیف پول خود را شارژ کنید."
    )


async def config_list_text(configs: list[dict]) -> str:
    e_dash = await pe("dashboard")
    if not configs:
        return f"{e_dash} <b>کانفیگ‌های من</b>\n\nکانفیگ فعالی ندارید."
    text = f"{e_dash} <b>کانفیگ‌های من</b>\n\n"
    for i, cfg in enumerate(configs, 1):
        status = "\u2705" if cfg["is_active"] else "\u274c"
        text += f"{status} کانفیگ #{cfg['id']} - انقضا: {cfg['expire_date'][:10]}\n"
    return text


async def admin_stats(user_count: int, config_count: int, revenue: float, pending: int, symbol: str = "تومان") -> str:
    e_stats = await pe("stats")
    e_users = await pe("users")
    e_configs = await pe("dashboard")
    e_money = await pe("money")
    e_clock = await pe("clock")
    return (
        f"{e_stats} <b>آمار ادمین</b>\n\n"
        f"{e_users} کل کاربران: {user_count}\n"
        f"{e_configs} کانفیگ‌های فعال: {config_count}\n"
        f"{e_money} درآمد کل: {revenue:,.0f} {symbol}\n"
        f"{e_clock} رسیدهای در انتظار: {pending}"
    )


async def receipt_info(receipt: dict, symbol: str = "تومان") -> str:
    e_list = await pe("list")
    e_owner = await pe("owner")
    e_money = await pe("money")
    e_cal = await pe("calendar")
    e_check = await pe("check")
    return (
        f"{e_list} <b>رسید #{receipt['id']}</b>\n\n"
        f"{e_owner} کاربر: @{receipt.get('username', 'N/A')} (ID: {receipt['user_id']})\n"
        f"{e_money} مبلغ: {receipt['amount']:,.0f} {symbol}\n"
        f"{e_cal} ارسال: {receipt['created_at']}\n"
        f"{e_check} وضعیت: {receipt['status']}"
    )


async def user_info(user: dict, symbol: str = "تومان") -> str:
    e_owner = await pe("owner")
    e_money = await pe("money")
    e_cal = await pe("calendar")
    banned_text = "بله" if user["is_banned"] else "خیر"
    return (
        f"{e_owner} <b>اطلاعات کاربر</b>\n\n"
        f"آیدی: <code>{user['id']}</code>\n"
        f"نام کاربری: @{user.get('username', 'N/A')}\n"
        f"نام: {user.get('first_name', 'N/A')}\n"
        f"{e_money} موجودی: {user['balance']:,.0f} {symbol}\n"
        f"{e_cal} تاریخ ثبت: {user['created_at']}\n"
        f"مسدود: {banned_text}"
    )


async def enter_amount() -> str:
    e = await pe("money")
    return f"{e} مبلغ پرداخت را وارد کنید (مثال: 50000):"


async def setting_updated(key: str, value: str) -> str:
    e = await pe("gear")
    return f"{e} <b>تنظیم به‌روزرسانی شد!</b>\n\n{key}: {value}"


async def confirm_approve(amount: float) -> str:
    return f"تایید رسید به مبلغ {amount:,.0f}؟"


async def confirm_reject() -> str:
    return "رد این رسید؟"


async def no_pending_receipts() -> str:
    e = await pe("check")
    return f"{e} رسید در انتظاری وجود ندارد."
