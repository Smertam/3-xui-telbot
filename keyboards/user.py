from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_setting, is_admin
from utils.premium_emoji import get_button_emoji_id


async def _btn(text: str, callback_data: str, emoji_name: str = None, style: str = None) -> InlineKeyboardButton:
    kwargs = {"text": text, "callback_data": callback_data}
    if emoji_name:
        eid = await get_button_emoji_id(emoji_name)
        if eid:
            kwargs["icon_custom_emoji_id"] = eid
    return InlineKeyboardButton(**kwargs)


async def main_menu(user_id: int = 0) -> InlineKeyboardMarkup:
    wallet = await get_setting("btn_wallet")
    free_test = await get_setting("btn_free_test")
    buy_config = await get_setting("btn_buy_config")
    my_configs = await get_setting("btn_my_configs")
    free_test_enabled = await get_setting("free_test_enabled")
    rows = [
        [await _btn(wallet, "wallet", "wallet")],
    ]
    if free_test_enabled == "1":
        rows[0].append(await _btn(free_test, "free_test", "free_test"))
    rows.append([await _btn(buy_config, "buy_config", "buy_config")])
    rows.append([await _btn(my_configs, "my_configs", "my_configs")])
    if user_id and await is_admin(user_id):
        btn = await get_setting("btn_admin_settings")
        rows.append([await _btn(btn, "admin_menu", "settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def wallet_menu() -> InlineKeyboardMarkup:
    topup = await get_setting("btn_topup")
    tx_history = await get_setting("btn_tx_history")
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [await _btn(topup, "topup", "money")],
            [await _btn(tx_history, "tx_history", "history")],
            [await _btn(back, "main_menu", "back")],
        ]
    )


async def payment_method_menu(plan_id: int) -> InlineKeyboardMarkup:
    wallet_btn = await get_setting("btn_wallet_payment") or "Pay with Wallet"
    c2c_btn = await get_setting("btn_c2c_payment") or "Card to Card"
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [await _btn(wallet_btn, f"pay_wallet_{plan_id}", "card")],
            [await _btn(c2c_btn, f"pay_c2c_{plan_id}", "card")],
            [await _btn(back, "buy_config", "back")],
        ]
    )


async def plans_menu() -> InlineKeyboardMarkup:
    from database import get_plans
    plans = await get_plans()
    symbol = await get_setting("currency_symbol") or "تومان"
    buttons = []
    for p in plans:
        buttons.append([InlineKeyboardButton(
            text=f"{p['name']} | {p['gb']}GB | {p['days']}D | {p['price']:,} {symbol}",
            callback_data=f"select_plan_{p['id']}",
        )])
    back = await get_setting("btn_back")
    buttons.append([await _btn(back, "main_menu", "back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def config_detail(config_id: int) -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [await _btn("Copy Link", f"copy_link_{config_id}", "copy")],
            [await _btn(back, "my_configs", "back")],
        ]
    )


async def back_to_menu() -> InlineKeyboardMarkup:
    back = await get_setting("btn_back_to_menu")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [await _btn(back, "main_menu", "back")]
        ]
    )
