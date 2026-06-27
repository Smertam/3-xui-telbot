import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_notified_today: set[int] = set()
_last_reset_date: str = ""


async def _deactivate_expired():
    from database import get_expired_active_configs, deactivate_config
    configs = await get_expired_active_configs()
    if configs:
        for c in configs:
            await deactivate_config(c["id"])
        logger.info("Deactivated %d expired configs", len(configs))


async def _send_expiry_reminders(bot):
    global _notified_today, _last_reset_date
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if today != _last_reset_date:
        _notified_today.clear()
        _last_reset_date = today

    from database import get_configs_expiring_soon
    configs = await get_configs_expiring_soon()
    for c in configs:
        uid = c["user_id"]
        if uid in _notified_today:
            continue

        expire = datetime.fromisoformat(c["expire_date"])
        days_left = max(1, (expire - datetime.utcnow()).days)
        symbol = "تومان"
        try:
            from database import get_setting
            symbol = await get_setting("currency_symbol") or symbol
        except Exception:
            pass

        try:
            await bot.send_message(
                chat_id=uid,
                text=(
                    f"\u23f0 <b>کانفیگ در حال انقضا</b>\n\n"
                    f"کانفیگ <b>#{c['id']}</b> شما در <b>{days_left} روز</b> منقضی می‌شود.\n"
                    f"برای ادامه اتصال، کانفیگ جدید بخرید!"
                ),
            )
            _notified_today.add(uid)
        except Exception:
            _notified_today.add(uid)


async def scheduler_loop(bot, interval: int = 300):
    logger.info("Scheduler started (interval=%ds)", interval)
    while True:
        try:
            await _deactivate_expired()
            await _send_expiry_reminders(bot)
        except Exception as e:
            logger.error("Scheduler error: %s", e)
        await asyncio.sleep(interval)
