from aiogram import Router, F, BaseMiddleware
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import time
from database import (
    add_user, get_user, get_user_configs, has_free_test, add_config,
    get_setting, is_admin, get_plan, add_receipt, get_admins, update_balance,
)
from api import panel_api
from keyboards.user import (
    main_menu, back_to_menu, plans_menu, payment_method_menu, config_detail,
    force_join_keyboard,
)
from utils.texts import (
    WELCOME_TEXT_DEFAULT, config_list_text, config_created, free_test_config, no_balance,
)
from utils.premium_emoji import pe, get_button_emoji_id
from utils.qr_generator import generate_qr

router = Router()

TEST_CONFIG_DAYS = 1


async def _is_channel_member(bot, user_id: int) -> bool:
    enabled = await get_setting("force_join_enabled")
    if enabled != "1":
        return True
    channel_id = await get_setting("required_channel_id")
    if not channel_id:
        return True
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return True


async def _send_force_join(bot, chat_id: int):
    channel_id = await get_setting("required_channel_id") or ""
    text = await get_setting("force_join_text") or "⚠️ برای استفاده از ربات، ابتدا باید در کانال ما عضو شوید!"
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=await force_join_keyboard(channel_id))


class ForceJoinMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: CallbackQuery, data: dict):
        if event.data == "check_membership":
            return await handler(event, data)
        if not await _is_channel_member(event.bot, event.from_user.id):
            fail_text = await get_setting("force_join_fail_text") or "⚠️ ابتدا در کانال عضو شوید!"
            await event.answer(fail_text, show_alert=True)
            return
        return await handler(event, data)


router.callback_query.middleware(ForceJoinMiddleware())


async def _start_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="▶️ شروع")]],
        resize_keyboard=True,
    )


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
    if not await _is_channel_member(message.bot, message.from_user.id):
        await _send_force_join(message.bot, message.from_user.id)
        return
    welcome = await get_setting("welcome_text") or WELCOME_TEXT_DEFAULT
    await message.answer(welcome, parse_mode="HTML", reply_markup=await _start_kb())
    await message.answer("منوی اصلی", reply_markup=await main_menu(message.from_user.id))


@router.message(F.text == "▶️ شروع")
async def btn_start(message: Message):
    await add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )
    if not await _is_channel_member(message.bot, message.from_user.id):
        await _send_force_join(message.bot, message.from_user.id)
        return
    welcome = await get_setting("welcome_text") or WELCOME_TEXT_DEFAULT
    await message.answer(welcome, parse_mode="HTML", reply_markup=await main_menu(message.from_user.id))


@router.callback_query(F.data == "check_membership")
async def cb_check_membership(callback: CallbackQuery):
    if await _is_channel_member(callback.bot, callback.from_user.id):
        try:
            await callback.message.delete()
        except Exception:
            pass
        welcome = await get_setting("welcome_text") or WELCOME_TEXT_DEFAULT
        await callback.message.answer(welcome, parse_mode="HTML", reply_markup=await _start_kb())
        await callback.message.answer("منوی اصلی", reply_markup=await main_menu(callback.from_user.id))
    else:
        fail_text = await get_setting("force_join_fail_text") or "❌ شما هنوز در کانال عضو نیستید! لطفاً ابتدا عضو شوید و سپس دوباره بررسی کنید."
        await callback.answer(fail_text, show_alert=True)


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
        photo=qr_img, caption=text, parse_mode="HTML", reply_markup=await back_to_menu(),
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
    email = f"c2c_{user_id}_{username}_{int(time.time())}"

    await callback.answer("در حال ساخت کانفیگ...", show_alert=False)
    result = await panel_api.create_config(email, days=plan["days"], total_gb=plan["gb"])
    if not result:
        await callback.message.edit_text("ساخت کانفیگ ناموفق بود. لطفاً دوباره تلاش کنید.", reply_markup=await back_to_menu())
        return

    await add_config(
        user_id=user_id, plan_id=plan_id, sub_link=result["sub_link"],
        uuid=result["uuid"], email=email, expire_date=result["expire_date"],
    )

    await update_balance(user_id, -plan["price"])

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
        photo=qr_img, caption=text, parse_mode="HTML", reply_markup=await back_to_menu(),
    )


@router.callback_query(F.data == "buy_config")
async def cb_buy_config(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("لطفاً ابتدا /start را بزنید", show_alert=True)
        return
    text = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "  🛒 <b>خرید کانفیگ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "  پلن مورد نظر خود را انتخاب کنید:"
    )
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=await plans_menu())
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=await plans_menu())


@router.callback_query(F.data.startswith("select_plan_"))
async def cb_select_plan(callback: CallbackQuery):
    plan_id = int(callback.data.split("_")[-1])
    plan = await get_plan(plan_id)
    if not plan:
        await callback.answer("پلن یافت نشد!", show_alert=True)
        return

    symbol = await get_setting("currency_symbol") or "تومان"
    text = (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  📦 <b>{plan['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"  📊 حجم: <b>{plan['gb']} GB</b>\n"
        f"  📅 مدت: <b>{plan['days']} روز</b>\n"
        f"  💰 قیمت: <b>{plan['price']:,} {symbol}</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"  روش پرداخت را انتخاب کنید:"
    )
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=await payment_method_menu(plan_id))
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=await payment_method_menu(plan_id))


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
        text = await no_balance(plan["price"], user["balance"], symbol)
        try:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=await back_to_menu())
        except Exception:
            await callback.message.answer(text, parse_mode="HTML", reply_markup=await back_to_menu())
        return

    from database import update_balance
    await update_balance(user_id, -plan["price"])

    username = user.get("username") or str(user_id)
    ts = int(time.time())
    email = f"user_{user_id}_{username}_{ts}"

    await callback.answer("در حال ساخت کانفیگ...", show_alert=False)
    result = await panel_api.create_config(email, days=plan["days"], total_gb=plan["gb"])
    if not result:
        await update_balance(user_id, plan["price"])
        try:
            await callback.message.edit_text(
                "ساخت کانفیگ ناموفق بود. موجودی بازگردانده شد.", reply_markup=await back_to_menu(),
            )
        except Exception:
            await callback.message.answer(
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
        photo=qr_img, caption=text, parse_mode="HTML", reply_markup=await back_to_menu(),
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

    await state.update_data(c2c_plan_id=plan_id)
    await state.set_state(C2CState.waiting_confirm)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
    from utils.premium_emoji import pe, get_button_emoji_id
    from keyboards.user import _btn

    copy_card_btn = InlineKeyboardButton(
        text="کپی شماره کارت",
        copy_text=CopyTextButton(text=card_number),
    )
    eid = await get_button_emoji_id("copy_number")
    if eid:
        copy_card_btn.icon_custom_emoji_id = eid

    copy_both_btn = InlineKeyboardButton(
        text="کپی مبلغ",
        copy_text=CopyTextButton(text=f"{plan['price']:,} {symbol}"),
    )
    eid = await get_button_emoji_id("copy_price")
    if eid:
        copy_both_btn.icon_custom_emoji_id = eid

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [copy_card_btn, copy_both_btn],
        [await _btn("پرداخت موفق", f"c2c_confirm_{plan_id}", "success", btn_id="c2c_confirm")],
        [await _btn("لغو", "main_menu", "cancel", "danger", "cancel")],
    ])

    from utils.texts import c2c_payment_text
    text = await c2c_payment_text(plan, symbol, card_number, card_owner)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("c2c_confirm_"))
async def cb_c2c_confirm(callback: CallbackQuery, state: FSMContext):
    plan_id = int(callback.data.split("_")[-1])
    await state.update_data(c2c_plan_id=plan_id)
    await state.set_state(C2CState.waiting_photo)

    from utils.texts import c2c_upload_photo_text
    text = await c2c_upload_photo_text()
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=await back_to_menu())


@router.message(C2CState.waiting_photo, F.photo)
async def cb_c2c_receipt_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    plan_id = data.get("c2c_plan_id", 0)
    plan = await get_plan(plan_id)

    if not plan:
        await message.answer("پلن یافت نشد. لطفاً دوباره تلاش کنید.", reply_markup=await back_to_menu())
        await state.clear()
        return

    photo_file_id = message.photo[-1].file_id
    await add_receipt(message.from_user.id, plan["price"], photo_file_id, plan_id)
    await state.clear()

    symbol = await get_setting("currency_symbol") or "تومان"
    from utils.texts import c2c_receipt_submitted_text
    text = await c2c_receipt_submitted_text(plan, symbol)
    await message.answer(text, parse_mode="HTML", reply_markup=await back_to_menu())

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
        from keyboards.user import _btn
        buttons = []
        for cfg in active_configs[:5]:
            buttons.append([InlineKeyboardButton(
                text=f"\U0001f7e2 Config #{cfg['id']} \u2014 Exp: {cfg['expire_date'][:10]}",
                callback_data=f"config_detail_{cfg['id']}",
            )])
        btn_back = await get_setting("btn_back")
        buttons.append([await _btn(btn_back, "main_menu", "back", btn_id="back")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=await back_to_menu())


@router.callback_query(F.data.startswith("config_detail_"))
async def cb_config_detail(callback: CallbackQuery):
    config_id = int(callback.data.split("_")[-1])
    from database import get_db
    db = await get_db()
    cursor = await db.execute("SELECT * FROM configs WHERE id = ?", (config_id,))
    cfg = await cursor.fetchone()
    await db.close()

    if not cfg:
        await callback.answer("کانفیگ یافت نشد!", show_alert=True)
        return

    cfg = dict(cfg)
    sub_link = cfg["sub_link"]

    try:
        client_configs = await panel_api.get_client_configs(cfg["email"])
    except Exception:
        client_configs = []

    if client_configs:
        text = (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"  🔑 <b>کانفیگ #{cfg['id']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"  ⏰ انقضا: <b>{cfg['expire_date'][:10]}</b>\n"
            f"  📧 ایمیل: <code>{cfg['email']}</code>\n\n"
        )
        for cc in client_configs:
            text += f"━━━━━━━━━━━━━━━━━━━━\n"
            text += f"  📡 <b>{cc['tag']}</b> ({cc['protocol']})\n\n"
            text += f"  <code>{cc['config_link']}</code>\n\n"
        text += f"━━━━━━━━━━━━━━━━━━━━\n"
        text += f"  🔗 <b>لینک اشتراک:</b>\n"
        text += f"  <code>{sub_link}</code>\n"
        text += f"━━━━━━━━━━━━━━━━━━━━"

        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            text, parse_mode="HTML",
            reply_markup=await config_detail(config_id),
        )
    else:
        text = (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"  🔑 <b>کانفیگ #{cfg['id']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"  ⏰ انقضا: <b>{cfg['expire_date'][:10]}</b>\n"
            f"  📧 ایمیل: <code>{cfg['email']}</code>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"  🔗 <b>لینک اشتراک:</b>\n"
            f"  <code>{sub_link}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"QR کد را اسکن کنید یا لینک بالا را کپی نمایید."
        )
        qr_img = generate_qr(sub_link)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer_photo(
            photo=qr_img, caption=text, parse_mode="HTML",
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
        await callback.answer(f"لینک: {cfg['sub_link']}", show_alert=True)
    else:
        await callback.answer("کانفیگ یافت نشد!", show_alert=True)
