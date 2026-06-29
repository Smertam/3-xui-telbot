from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_setting, is_admin
from utils.premium_emoji import get_button_emoji_id


async def _btn(text: str, callback_data: str, emoji_name: str = None, style: str = None, btn_id: str = None) -> InlineKeyboardButton:
    kwargs = {"text": text, "callback_data": callback_data}
    if btn_id:
        db_emoji = await get_setting(f"btn_emoji_{btn_id}")
        if db_emoji:
            kwargs["icon_custom_emoji_id"] = db_emoji
        elif emoji_name:
            from utils.premium_emoji import get_button_emoji_id
            eid = await get_button_emoji_id(emoji_name)
            if eid:
                kwargs["icon_custom_emoji_id"] = eid
        db_style = await get_setting(f"btn_style_{btn_id}")
        if db_style:
            kwargs["style"] = db_style
        elif style:
            kwargs["style"] = style
    elif emoji_name:
        from utils.premium_emoji import get_button_emoji_id
        eid = await get_button_emoji_id(emoji_name)
        if eid:
            kwargs["icon_custom_emoji_id"] = eid
        if style:
            kwargs["style"] = style
    return InlineKeyboardButton(**kwargs)


async def main_menu(user_id: int = 0) -> InlineKeyboardMarkup:
    wallet = await get_setting("btn_wallet")
    free_test = await get_setting("btn_free_test")
    buy_config = await get_setting("btn_buy_config")
    my_configs = await get_setting("btn_my_configs")
    free_test_enabled = await get_setting("free_test_enabled")
    rows = [
        [await _btn(wallet, "wallet", "wallet", "primary", "wallet")],
    ]
    if free_test_enabled == "1":
        rows[0].append(await _btn(free_test, "free_test", "free_test", "primary", "free_test"))
    rows.append([await _btn(buy_config, "buy_config", "buy_config", "primary", "buy_config")])
    rows.append([await _btn(my_configs, "my_configs", "my_configs", "success", "my_configs")])
    if user_id and await is_admin(user_id):
        btn = await get_setting("btn_admin_settings")
        rows.append([await _btn(btn, "admin_menu", "settings", btn_id="admin_settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def wallet_menu() -> InlineKeyboardMarkup:
    topup = await get_setting("btn_topup")
    tx_history = await get_setting("btn_tx_history")
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [await _btn(topup, "topup", "money", btn_id="topup")],
            [await _btn(tx_history, "tx_history", "history", btn_id="tx_history")],
            [await _btn(back, "main_menu", "back", btn_id="back")],
        ]
    )


async def payment_method_menu(plan_id: int) -> InlineKeyboardMarkup:
    wallet_btn = await get_setting("btn_wallet_payment") or "Pay with Wallet"
    c2c_btn = await get_setting("btn_c2c_payment") or "Card to Card"
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [await _btn(wallet_btn, f"pay_wallet_{plan_id}", "card", btn_id="wallet_payment")],
            [await _btn(c2c_btn, f"pay_c2c_{plan_id}", "card", btn_id="c2c_payment")],
            [await _btn(back, "buy_config", "back", btn_id="back2")],
        ]
    )


async def plans_menu() -> InlineKeyboardMarkup:
    from database import get_plans
    plans = await get_plans()
    symbol = await get_setting("currency_symbol") or "تومان"
    buttons = []
    for p in plans:
        buttons.append([InlineKeyboardButton(
            text=f"\U0001f4e6 {p['name']} \u2014 {p['gb']}GB / {p['days']}D \u2014 {p['price']:,} {symbol}",
            callback_data=f"select_plan_{p['id']}",
        )])
    back = await get_setting("btn_back")
    buttons.append([await _btn(back, "main_menu", "back", btn_id="back3")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def config_detail(config_id: int) -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [await _btn("Copy Sub Link", f"copy_link_{config_id}", "copy", btn_id="copy_link")],
            [await _btn(back, "my_configs", "back", btn_id="back4")],
        ]
    )


async def force_join_keyboard(channel_id: str) -> InlineKeyboardMarkup:
    join_text = await get_setting("force_join_btn_join") or "🔗 عضویت در کانال"
    check_text = await get_setting("force_join_btn_check") or "✅ بررسی عضویت"
    check_btn = await _btn(check_text, "check_membership", "check", btn_id="force_join_check")

    url = None
    if channel_id.startswith("@"):
        url = f"https://t.me/{channel_id.lstrip('@')}"
    elif channel_id.startswith("-"):
        try:
            import state
            if state.bot_instance:
                chat = await state.bot_instance.get_chat(channel_id)
                if chat.username:
                    url = f"https://t.me/{chat.username}"
        except Exception:
            pass
    else:
        url = f"https://t.me/{channel_id}"

    buttons = []
    if url:
        join_kwargs = {"text": join_text, "url": url}
        eid = await get_button_emoji_id("link")
        if eid:
            join_kwargs["icon_custom_emoji_id"] = eid
        db_style = await get_setting("btn_style_force_join_join")
        if db_style:
            join_kwargs["style"] = db_style
        buttons.append([InlineKeyboardButton(**join_kwargs)])
    buttons.append([check_btn])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def back_to_menu() -> InlineKeyboardMarkup:
    back = await get_setting("btn_back_to_menu")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [await _btn(back, "main_menu", "back", btn_id="back_to_menu")]
        ]
    )


BUTTON_CONFIGS = {
    "wallet": {"label": "Wallet", "default_style": "primary", "default_emoji": "wallet"},
    "free_test": {"label": "Free Test", "default_style": "primary", "default_emoji": "free_test"},
    "buy_config": {"label": "Buy Config", "default_style": "primary", "default_emoji": "buy_config"},
    "my_configs": {"label": "My Configs", "default_style": "success", "default_emoji": "my_configs"},
    "topup": {"label": "Top Up", "default_style": "", "default_emoji": "money"},
    "tx_history": {"label": "Transaction History", "default_style": "", "default_emoji": "history"},
    "back": {"label": "Back", "default_style": "", "default_emoji": "back"},
    "back_to_menu": {"label": "Back to Menu", "default_style": "", "default_emoji": "back"},
    "wallet_payment": {"label": "Pay with Wallet", "default_style": "", "default_emoji": "card"},
    "c2c_payment": {"label": "Card to Card", "default_style": "", "default_emoji": "card"},
    "copy_link": {"label": "Copy Link", "default_style": "", "default_emoji": "copy"},
    "copy_number": {"label": "Copy Card Number", "default_style": "", "default_emoji": "copy_number"},
    "copy_price": {"label": "Copy Price", "default_style": "", "default_emoji": "copy_price"},
    "c2c_confirm": {"label": "Payment Success (C2C)", "default_style": "success", "default_emoji": "success"},
    "topup_confirm": {"label": "Payment Success (TopUp)", "default_style": "success", "default_emoji": "success"},
    "cancel": {"label": "Cancel", "default_style": "danger", "default_emoji": "cancel"},
    "make_config": {"label": "Make My Config", "default_style": "primary", "default_emoji": "package"},
    "force_join_join": {"label": "Join Channel", "default_style": "primary", "default_emoji": "link"},
    "force_join_check": {"label": "Check Membership", "default_style": "success", "default_emoji": "check"},
    "admin_stats": {"label": "Admin - Statistics", "default_style": "", "default_emoji": "stats"},
    "admin_receipts": {"label": "Admin - Receipts", "default_style": "", "default_emoji": "receipts"},
    "admin_users": {"label": "Admin - Users", "default_style": "", "default_emoji": "users"},
    "admin_settings": {"label": "Admin - Settings", "default_style": "", "default_emoji": "settings"},
    "admin_admins": {"label": "Admin - Admins", "default_style": "", "default_emoji": "admins"},
    "admin_plans": {"label": "Admin - Plans", "default_style": "", "default_emoji": "plans"},
    "admin_broadcast": {"label": "Admin - Broadcast", "default_style": "", "default_emoji": "list"},
    "admin_panel_info": {"label": "Admin - Panel Info", "default_style": "", "default_emoji": "gear"},
    "approve": {"label": "Approve Receipt", "default_style": "success", "default_emoji": "approve"},
    "reject": {"label": "Reject Receipt", "default_style": "danger", "default_emoji": "reject"},
    "add_balance": {"label": "Add Balance", "default_style": "success", "default_emoji": "plus"},
    "remove_balance": {"label": "Remove Balance", "default_style": "danger", "default_emoji": "minus"},
    "ban": {"label": "Ban User", "default_style": "danger", "default_emoji": "ban"},
    "unban": {"label": "Unban User", "default_style": "success", "default_emoji": "unban"},
    "view_configs": {"label": "View Configs", "default_style": "", "default_emoji": "list"},
    "add_admin": {"label": "Add Admin", "default_style": "success", "default_emoji": "plus"},
    "remove_admin": {"label": "Remove Admin", "default_style": "danger", "default_emoji": "minus"},
    "list_admins": {"label": "List Admins", "default_style": "", "default_emoji": "list"},
    "add_plan": {"label": "Add Plan", "default_style": "success", "default_emoji": "plus"},
    "edit_plan": {"label": "Edit Plan", "default_style": "", "default_emoji": "gear"},
    "delete_plan": {"label": "Delete Plan", "default_style": "danger", "default_emoji": "cross"},
    "edit_welcome": {"label": "Edit Welcome Text", "default_style": "", "default_emoji": "gear"},
    "edit_buttons": {"label": "Edit Button Names", "default_style": "", "default_emoji": "gear"},
    "edit_currency": {"label": "Change Currency", "default_style": "", "default_emoji": "gear"},
    "edit_card_number": {"label": "Card Number", "default_style": "", "default_emoji": "card"},
    "edit_card_owner": {"label": "Card Owner Name", "default_style": "", "default_emoji": "owner"},
    "edit_free_test_mb": {"label": "Free Test Volume", "default_style": "", "default_emoji": "gear"},
    "toggle_free_test": {"label": "Toggle Free Test", "default_style": "", "default_emoji": "gear"},
    "edit_auto_approve": {"label": "Auto-Approve Limit", "default_style": "", "default_emoji": "gear"},
    "edit_premium_emojis": {"label": "Premium Emojis", "default_style": "", "default_emoji": "gear"},
    "send_emoji_register": {"label": "Send Premium Emoji", "default_style": "", "default_emoji": "star"},
    "view_emojis": {"label": "View Registered Emojis", "default_style": "", "default_emoji": "list"},
    "clear_emojis": {"label": "Clear All Emojis", "default_style": "danger", "default_emoji": "cross"},
}
