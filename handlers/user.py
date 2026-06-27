from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import time
from database import (
    add_user, get_user, get_user_configs, has_free_test, add_config,
    get_setting, is_admin, get_plan, add_receipt, get_admins,
)
from api import panel_api
from keyboards.user import (
    main_menu, back_to_menu, plans_menu, payment_method_menu, config_detail,
)
from utils.texts import (
    WELCOME_TEXT, config_list_text, config_created, free_test_config, no_balance,
)
from utils.qr_generator import generate_qr

router = Router()

TEST_CONFIG_DAYS = 1


class C2CState(StatesGroup):
    waiting_confirm = State()
    waiting_photo = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )
    welcome = await get_setting("welcome_text") or WELCOME_TEXT
    await message.answer(welcome, reply_markup=await main_menu(message.from_user.id))


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("منوی اصلی", reply_markup=await main_menu(message.from_user.id))


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_text("منوی اصلی", reply_markup=await main_menu(callback.from_user.id))
    except Exception:
        await callback.message.answer("منوی اصلی", reply_markup=await main_menu(callback.from_user.id))


@router.callback_query(F.data == "free_test")
async def cb_free_test(callback: CallbackQuery):
    user_id = callback.from_user.id
    free_test_enabled = await get_setting("free_test_enabled")
    if free_test_enabled != "1":
        await callback.answer("Free test is currently disabled.", show_alert=True)
        return
    admin = await is_admin(user_id)
    if not admin and await has_free_test(user_id):
        await callback.answer("You already used your free test!", show_alert=True)
        return

    user = await get_user(user_id)
    if not user:
        await callback.answer("لطفاً ابتدا /start را بزنید", show_alert=True)
        return

    username = user.get("username") or str(user_id)
    ts = int(time.time())
    suffix = f"_{user_id}_{ts}" if admin else f"_test_{user_id}_{username}_{ts}"
    email = f"free{suffix}"

    await callback.answer("در حال ساخت کانفیگ رایگان...", show_alert=False)
    free_test_mb = int(await get_setting("free_test_mb") or "102400")
    result = await panel_api.create_test_config(email, total_mb=free_test_mb)
    if not result:
        await callback.message.edit_text(
            "ساخت کانفیگ ناموفق بود. لطفاً با ادمین تماس بگیرید.", reply_markup=await back_to_menu()
        )
        return

    await add_config(
        user_id=user_id,
        plan_id=0,
        sub_link=result["sub_link"],
        uuid=result["uuid"],
        email=email,
        expire_date=result["expire_date"],
    )

    text = await free_test_config(result["sub_link"], TEST_CONFIG_DAYS)
    qr_img = generate_qr(result["sub_link"])

    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer_photo(
        photo=qr_img, caption=text, parse_mode="Markdown", reply_markup=await back_to_menu(),
    )


@router.callback_query(F.data.startswith("make_config_"))
async def cb_make_config(callback: CallbackQuery):
    plan_id = int(callback.data.split("_")[-1])
    plan = await get_plan(plan_id)
    if not plan:
        await callback.answer("پلن یافت نشد!", show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)
    username = user.get("username") or str(user_id)
    email = f"c2c_{user_id}_{username}"

    await callback.answer("در حال ساخت کانفیگ...", show_alert=False)
    result = await panel_api.create_config(email, days=plan["days"], total_gb=plan["gb"])
    if not result:
        await callback.message.edit_text("ساخت کانفیگ ناموفق بود. لطفاً دوباره تلاش کنید.", reply_markup=await back_to_menu())
        return

    await add_config(
        user_id=user_id, plan_id=plan_id, sub_link=result["sub_link"],
        uuid=result["uuid"], email=email, expire_date=result["expire_date"],
    )

    symbol = await get_setting("currency_symbol") or "تومان"
    text = await config_created(
        result["sub_link"], result["expire_date"][:10],
        plan["price"], plan["name"], plan["gb"], plan["days"], symbol,
    )
    qr_img = generate_qr(result["sub_link"])

    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer_photo(
        photo=qr_img, caption=text, parse_mode="Markdown", reply_markup=await back_to_menu(),
    )


@router.callback_query(F.data == "buy_config")
async def cb_buy_config(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("لطفاً ابتدا /start را بزنید", show_alert=True)
        return
    await callback.message.edit_text(
        "**یک پلن انتخاب کنید:**\n\nپلن مورد نظر خود را انتخاب کنید.",
        parse_mode="Markdown",
        reply_markup=await plans_menu(),
    )


@router.callback_query(F.data.startswith("select_plan_"))
async def cb_select_plan(callback: CallbackQuery):
    plan_id = int(callback.data.split("_")[-1])
    plan = await get_plan(plan_id)
    if not plan:
        await callback.answer("پلن یافت نشد!", show_alert=True)
        return

    symbol = await get_setting("currency_symbol") or "تومان"
    await callback.message.edit_text(
        f"**{plan['name']}**\n\n"
        f"\U0001f4ca Volume: {plan['gb']}GB\n"
        f"\U0001f4c5 Duration: {plan['days']} days\n"
        f"\U0001f4b0 Price: {plan['price']:,} {symbol}\n\n"
        f"**Choose payment method:**",
        parse_mode="Markdown",
        reply_markup=await payment_method_menu(plan_id),
    )


@router.callback_query(F.data.startswith("pay_wallet_"))
async def cb_pay_wallet(callback: CallbackQuery):
    plan_id = int(callback.data.split("_")[-1])
    plan = await get_plan(plan_id)
    if not plan:
        await callback.answer("پلن یافت نشد!", show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)
    symbol = await get_setting("currency_symbol") or "تومان"

    if user["balance"] < plan["price"]:
        await callback.message.edit_text(
            await no_balance(plan["price"], user["balance"], symbol),
            reply_markup=await back_to_menu(),
        )
        return

    from database import update_balance
    await update_balance(user_id, -plan["price"])

    username = user.get("username") or str(user_id)
    email = f"user_{user_id}_{username}"

    await callback.answer("در حال ساخت کانفیگ...", show_alert=False)
    result = await panel_api.create_config(email, days=plan["days"], total_gb=plan["gb"])
    if not result:
        await update_balance(user_id, plan["price"])
        await callback.message.edit_text(
            "ساخت کانفیگ ناموفق بود. موجودی بازگردانده شد.", reply_markup=await back_to_menu(),
        )
        return

    await add_config(
        user_id=user_id, plan_id=plan_id, sub_link=result["sub_link"],
        uuid=result["uuid"], email=email, expire_date=result["expire_date"],
    )

    text = await config_created(result["sub_link"], result["expire_date"][:10], plan["price"], plan["name"], plan["gb"], plan["days"], symbol)
    qr_img = generate_qr(result["sub_link"])

    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer_photo(
        photo=qr_img, caption=text, parse_mode="Markdown", reply_markup=await back_to_menu(),
    )


@router.callback_query(F.data.startswith("pay_c2c_"))
async def cb_pay_c2c(callback: CallbackQuery, state: FSMContext):
    plan_id = int(callback.data.split("_")[-1])
    plan = await get_plan(plan_id)
    if not plan:
        await callback.answer("پلن یافت نشد!", show_alert=True)
        return

    symbol = await get_setting("currency_symbol") or "تومان"
    card_number = await get_setting("card_number") or "1234-5678-9012-3456"
    card_owner = await get_setting("card_owner") or "Card Owner"
    c2c_title = await get_setting("c2c_title") or "Card to Card Payment"

    await state.update_data(c2c_plan_id=plan_id)
    await state.set_state(C2CState.waiting_confirm)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"پرداخت موفق", callback_data=f"c2c_confirm_{plan_id}")],
        [InlineKeyboardButton(text="لغو", callback_data="main_menu")],
    ])

    await callback.message.edit_text(
        f"**{c2c_title}**\n\n"
        f"Plan: **{plan['name']}** ({plan['gb']}GB / {plan['days']} days)\n"
        f"Amount: **{plan['price']:,} {symbol}**\n\n"
        f"Card Number: `{card_number}`\n"
        f"Card Owner: **{card_owner}**\n\n"
        f"Send the exact amount to the card above, then click **Payment Success** to upload your receipt.",
        parse_mode="Markdown",
        reply_markup=kb,
    )


@router.callback_query(F.data.startswith("c2c_confirm_"))
async def cb_c2c_confirm(callback: CallbackQuery, state: FSMContext):
    plan_id = int(callback.data.split("_")[-1])
    await state.update_data(c2c_plan_id=plan_id)
    await state.set_state(C2CState.waiting_photo)

    await callback.message.edit_text(
        "رسید پرداخت خود را آپلود کنید.",
        reply_markup=await back_to_menu(),
    )


@router.message(C2CState.waiting_photo, F.photo)
async def cb_c2c_receipt_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    plan_id = data.get("c2c_plan_id", 0)
    plan = await get_plan(plan_id)

    if not plan:
        await message.answer("Plan not found. Please try again.", reply_markup=await back_to_menu())
        await state.clear()
        return

    photo_file_id = message.photo[-1].file_id
    await add_receipt(message.from_user.id, plan["price"], photo_file_id, plan_id)
    await state.clear()

    symbol = await get_setting("currency_symbol") or "تومان"
    await message.answer(
        f"\u2705 **Receipt submitted!**\n\n"
        f"Plan: **{plan['name']}** ({plan['gb']}GB / {plan['days']} days)\n"
        f"Amount: **{plan['price']:,} {symbol}**\n\n"
        f"Admins will review your receipt. You will receive your config automatically once approved.",
        parse_mode="Markdown",
        reply_markup=await back_to_menu(),
    )

    admins = await get_admins()
    for admin in admins:
        try:
            await message.bot.send_photo(
                chat_id=admin["user_id"],
                photo=photo_file_id,
                caption=(
                    f"**New C2C Receipt**\n\n"
                    f"User: @{message.from_user.username or 'N/A'} (ID: {message.from_user.id})\n"
                    f"Plan: {plan['name']} ({plan['gb']}GB / {plan['days']} days)\n"
                    f"Amount: {plan['price']:,} {symbol}\n\n"
                    f"Use /admin to review."
                ),
                parse_mode="Markdown",
            )
        except Exception:
            pass


@router.callback_query(F.data == "cancel_receipt")
async def cb_cancel_receipt(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Payment cancelled.", reply_markup=await back_to_menu())


@router.callback_query(F.data == "my_configs")
async def cb_my_configs(callback: CallbackQuery):
    user_id = callback.from_user.id
    configs = await get_user_configs(user_id)

    active_configs = [c for c in configs if c["is_active"]]
    text = await config_list_text(active_configs)

    if active_configs:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        buttons = []
        for cfg in active_configs[:5]:
            buttons.append([InlineKeyboardButton(
                text=f"\U0001f511 Config #{cfg['id']} - Exp: {cfg['expire_date'][:10]}",
                callback_data=f"config_detail_{cfg['id']}",
            )])
        btn_back = await get_setting("btn_back")
        buttons.append([InlineKeyboardButton(text=btn_back, callback_data="main_menu")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=await back_to_menu())


@router.callback_query(F.data.startswith("config_detail_"))
async def cb_config_detail(callback: CallbackQuery):
    config_id = int(callback.data.split("_")[-1])
    from database import get_db
    db = await get_db()
    cursor = await db.execute("SELECT * FROM configs WHERE id = ?", (config_id,))
    cfg = await cursor.fetchone()
    await db.close()

    if not cfg:
        await callback.answer("Config not found!", show_alert=True)
        return

    cfg = dict(cfg)
    sub_link = cfg["sub_link"]
    text = (
        f"**Config #{cfg['id']}**\n\n"
        f"Sub Link:\n`{sub_link}`\n\n"
        f"Expires: {cfg['expire_date'][:10]}\n"
        f"Email: `{cfg['email']}`\n"
    )

    try:
        client_configs = await panel_api.get_client_configs(cfg["email"])
        if client_configs:
            text += f"\n**Protocols inside:**\n"
            for cc in client_configs:
                text += f"  {cc['protocol']} - {cc['tag']} (ID: {cc['inbound_id']})\n"
    except Exception:
        pass

    text += f"\nScan the QR code or copy the link above."
    qr_img = generate_qr(sub_link)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer_photo(
        photo=qr_img, caption=text, parse_mode="Markdown",
        reply_markup=await config_detail(config_id),
    )


@router.callback_query(F.data.startswith("copy_link_"))
async def cb_copy_link(callback: CallbackQuery):
    config_id = int(callback.data.split("_")[-1])
    from database import get_db
    db = await get_db()
    cursor = await db.execute("SELECT sub_link FROM configs WHERE id = ?", (config_id,))
    cfg = await cursor.fetchone()
    await db.close()

    if cfg:
        await callback.answer(f"Link: {cfg['sub_link']}", show_alert=True)
    else:
        await callback.answer("Config not found!", show_alert=True)
