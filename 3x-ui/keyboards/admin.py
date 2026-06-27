from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_setting


async def admin_menu() -> InlineKeyboardMarkup:
    stats = await get_setting("btn_admin_stats")
    receipts = await get_setting("btn_admin_receipts")
    users = await get_setting("btn_admin_users")
    settings = await get_setting("btn_admin_settings")
    admins = await get_setting("btn_admin_admins")
    plans = await get_setting("btn_admin_plans") or "Plans"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=stats, callback_data="admin_stats")],
            [InlineKeyboardButton(text=plans, callback_data="admin_plans")],
            [InlineKeyboardButton(text=receipts, callback_data="pending_receipts")],
            [InlineKeyboardButton(text=users, callback_data="admin_users")],
            [InlineKeyboardButton(text="Broadcast", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text=settings, callback_data="admin_settings")],
            [InlineKeyboardButton(text=admins, callback_data="manage_admins")],
        ]
    )


async def receipt_actions(receipt_id: int) -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Approve", callback_data=f"approve_{receipt_id}"),
                InlineKeyboardButton(text="Reject", callback_data=f"reject_{receipt_id}"),
            ],
            [InlineKeyboardButton(text=back, callback_data="admin_menu")],
        ]
    )


async def user_actions(user_id: int) -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="View Configs", callback_data=f"admin_cfgs_{user_id}")],
            [
                InlineKeyboardButton(text="+ Add Balance", callback_data=f"add_bal_{user_id}"),
                InlineKeyboardButton(text="- Remove Balance", callback_data=f"rem_bal_{user_id}"),
            ],
            [
                InlineKeyboardButton(text="Ban", callback_data=f"ban_{user_id}"),
                InlineKeyboardButton(text="Unban", callback_data=f"unban_{user_id}"),
            ],
            [InlineKeyboardButton(text=back, callback_data="admin_users")],
        ]
    )


async def admin_settings_menu() -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    free_test_status = await get_setting("free_test_enabled")
    ft_label = "Disable Free Test" if free_test_status == "1" else "Enable Free Test"
    ft_callback = "toggle_free_test"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Edit Welcome Text", callback_data="edit_welcome")],
            [InlineKeyboardButton(text="Edit Button Names", callback_data="edit_buttons")],
            [InlineKeyboardButton(text="Change Currency Symbol", callback_data="edit_currency")],
            [InlineKeyboardButton(text="Card Number", callback_data="edit_card_number")],
            [InlineKeyboardButton(text="Card Owner Name", callback_data="edit_card_owner")],
            [InlineKeyboardButton(text=f"Free Test Volume", callback_data="edit_free_test_mb")],
            [InlineKeyboardButton(text=ft_label, callback_data=ft_callback)],
            [InlineKeyboardButton(text="Auto-Approve Limit", callback_data="edit_auto_approve")],
            [InlineKeyboardButton(text="Premium Emojis", callback_data="edit_premium_emojis")],
            [InlineKeyboardButton(text=back, callback_data="admin_menu")],
        ]
    )


async def buttons_menu() -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    btn_wallet = await get_setting("btn_wallet")
    btn_free_test = await get_setting("btn_free_test")
    btn_buy = await get_setting("btn_buy_config")
    btn_configs = await get_setting("btn_my_configs")
    btn_topup = await get_setting("btn_topup")
    btn_history = await get_setting("btn_tx_history")
    btn_back_menu = await get_setting("btn_back_to_menu")
    btn_stats = await get_setting("btn_admin_stats")
    btn_receipts = await get_setting("btn_admin_receipts")
    btn_users = await get_setting("btn_admin_users")
    btn_settings = await get_setting("btn_admin_settings")
    btn_admins = await get_setting("btn_admin_admins")
    btn_plans = await get_setting("btn_admin_plans")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Wallet: {btn_wallet}", callback_data="edit_btn_wallet")],
            [InlineKeyboardButton(text=f"Free Test: {btn_free_test}", callback_data="edit_btn_free_test")],
            [InlineKeyboardButton(text=f"Buy Config: {btn_buy}", callback_data="edit_btn_buy_config")],
            [InlineKeyboardButton(text=f"My Configs: {btn_configs}", callback_data="edit_btn_my_configs")],
            [InlineKeyboardButton(text=f"Top Up: {btn_topup}", callback_data="edit_btn_topup")],
            [InlineKeyboardButton(text=f"History: {btn_history}", callback_data="edit_btn_tx_history")],
            [InlineKeyboardButton(text=f"Back: {back}", callback_data="edit_btn_back")],
            [InlineKeyboardButton(text=f"Back Menu: {btn_back_menu}", callback_data="edit_btn_back_to_menu")],
            [InlineKeyboardButton(text=f"Stats: {btn_stats}", callback_data="edit_btn_admin_stats")],
            [InlineKeyboardButton(text=f"Receipts: {btn_receipts}", callback_data="edit_btn_admin_receipts")],
            [InlineKeyboardButton(text=f"Users: {btn_users}", callback_data="edit_btn_admin_users")],
            [InlineKeyboardButton(text=f"Settings: {btn_settings}", callback_data="edit_btn_admin_settings")],
            [InlineKeyboardButton(text=f"Admins: {btn_admins}", callback_data="edit_btn_admin_admins")],
            [InlineKeyboardButton(text=f"Plans: {btn_plans}", callback_data="edit_btn_admin_plans")],
            [InlineKeyboardButton(text=back, callback_data="admin_settings")],
        ]
    )


async def plans_management_menu() -> InlineKeyboardMarkup:
    from database import get_all_plans
    plans = await get_all_plans()
    symbol = await get_setting("currency_symbol") or "تومان"
    buttons = []
    for p in plans:
        status = "+" if p["is_active"] else "x"
        buttons.append([InlineKeyboardButton(
            text=f"[{status}] {p['name']} | {p['gb']}GB | {p['days']}D | {p['price']:,} {symbol}",
            callback_data=f"plan_detail_{p['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="+ Add Plan", callback_data="add_plan")])
    back = await get_setting("btn_back")
    buttons.append([InlineKeyboardButton(text=back, callback_data="admin_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def plan_actions(plan_id: int) -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Edit Plan", callback_data=f"edit_plan_{plan_id}")],
            [InlineKeyboardButton(text="Delete Plan", callback_data=f"delete_plan_{plan_id}")],
            [InlineKeyboardButton(text=back, callback_data="admin_plans")],
        ]
    )


async def back_to_admin() -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=back, callback_data="admin_menu")]
        ]
    )


async def manage_admins_menu() -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="+ Add Admin", callback_data="add_admin")],
            [InlineKeyboardButton(text="- Remove Admin", callback_data="remove_admin")],
            [InlineKeyboardButton(text="List Admins", callback_data="list_admins")],
            [InlineKeyboardButton(text=back, callback_data="admin_menu")],
        ]
    )


async def premium_emojis_menu() -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Send Premium Emoji", callback_data="send_emoji_register")],
            [InlineKeyboardButton(text="View Registered Emojis", callback_data="view_emojis")],
            [InlineKeyboardButton(text="Clear All Emojis", callback_data="clear_emojis")],
            [InlineKeyboardButton(text=back, callback_data="admin_settings")],
        ]
    )


async def user_config_list(configs: list, user_id: int) -> InlineKeyboardMarkup:
    buttons = []
    for c in configs[:10]:
        status = "Active" if c["is_active"] else "Expired"
        buttons.append([InlineKeyboardButton(
            text=f"Config #{c['id']} ({status})",
            callback_data=f"admin_cfg_{c['id']}_{user_id}",
        )])
    back = await get_setting("btn_back")
    buttons.append([InlineKeyboardButton(text=back, callback_data=f"view_user_{user_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def config_detail_actions(config_id: int, user_id: int) -> InlineKeyboardMarkup:
    back = await get_setting("btn_back")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Delete Config", callback_data=f"admin_del_cfg_{config_id}_{user_id}")],
            [InlineKeyboardButton(text=back, callback_data=f"admin_cfgs_{user_id}")],
        ]
    )
