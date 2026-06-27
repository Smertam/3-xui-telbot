from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_user, add_receipt, get_setting, get_admins
from keyboards.user import wallet_menu, back_to_menu
from utils.texts import wallet_text, receipt_submitted, enter_amount

router = Router()


class TopUpState(StatesGroup):
    waiting_amount = State()
    waiting_photo = State()


@router.callback_query(F.data == "wallet")
async def cb_wallet(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("لطفاً ابتدا /start را بزنید", show_alert=True)
        return
    symbol = await get_setting("currency_symbol") or "تومان"
    text = await wallet_text(user["balance"], symbol)
    await callback.message.edit_text(
        text,
        reply_markup=await wallet_menu(),
    )


@router.callback_query(F.data == "topup")
async def cb_topup(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TopUpState.waiting_amount)
    await callback.message.edit_text(
        await enter_amount(),
        reply_markup=await back_to_menu(),
    )


@router.message(TopUpState.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("مبلغ نامعتبر. یک عدد مثبت وارد کنید (مثال: 50000):")
        return

    min_topup = float(await get_setting("min_topup") or "50000")
    if amount < min_topup:
        symbol = await get_setting("currency_symbol") or "تومان"
        await message.answer(f"حداقل شارژ {min_topup:,.0f} {symbol} است. دوباره تلاش کنید:")
        return

    await state.update_data(amount=amount)
    await state.set_state(TopUpState.waiting_photo)
    symbol = await get_setting("currency_symbol") or "تومان"
    await message.answer(
        f"مبلغ: **{amount:,.0f} {symbol}**\n\nاکنون اسکرین‌شات رسید پرداخت خود را آپلود کنید.",
        parse_mode="Markdown",
        reply_markup=await back_to_menu(),
    )


@router.message(TopUpState.waiting_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount", 0)
    photo_file_id = message.photo[-1].file_id

    await add_receipt(message.from_user.id, amount, photo_file_id, plan_id=0)
    await state.clear()
    symbol = await get_setting("currency_symbol") or "تومان"

    auto_max = float(await get_setting("auto_approve_max") or "0")
    if auto_max > 0 and amount <= auto_max:
        from database import approve_receipt, get_user, get_pending_receipts
        pending = await get_pending_receipts()
        receipt = None
        for r in pending:
            if r["user_id"] == message.from_user.id and abs(r["amount"] - amount) < 0.01:
                receipt = r
                break
        if receipt:
            await approve_receipt(receipt["id"], 0)
            user = await get_user(message.from_user.id)
            new_balance = user["balance"] if user else 0
            from utils.texts import receipt_approved
            await message.answer(
                await receipt_approved(amount, new_balance, symbol),
                reply_markup=await back_to_menu(),
            )
        else:
            await message.answer(
                await receipt_submitted(amount, symbol),
                reply_markup=await back_to_menu(),
            )
    else:
        await message.answer(
            await receipt_submitted(amount, symbol),
            reply_markup=await back_to_menu(),
        )

    admins = await get_admins()
    for admin in admins:
        try:
            await message.bot.send_photo(
                chat_id=admin["user_id"],
                photo=photo_file_id,
                caption=(
                    f"**New Receipt** (Top Up)\n\n"
                    f"User: @{message.from_user.username or 'N/A'} (ID: {message.from_user.id})\n"
                    f"Amount: {amount:,.0f} {symbol}\n\n"
                    f"Use /admin to review."
                ),
                parse_mode="Markdown",
            )
        except Exception:
            pass


@router.callback_query(F.data == "cancel_receipt")
async def cb_cancel_receipt(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("رسید لغو شد.", reply_markup=await back_to_menu())


@router.callback_query(F.data == "tx_history")
async def cb_tx_history(callback: CallbackQuery):
    from database import get_db
    symbol = await get_setting("currency_symbol") or "تومان"
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM receipts WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (callback.from_user.id,),
    )
    receipts = await cursor.fetchall()
    await db.close()

    if not receipts:
        await callback.message.edit_text(
            "**تاریخچه تراکنش**\n\nهیچ تراکنشی ثبت نشده.",
            parse_mode="Markdown",
            reply_markup=await back_to_menu(),
        )
        return

    text = "**تاریخچه تراکنش**\n\n"
    for r in receipts:
        status_icon = {"pending": "در انتظار", "approved": "تایید شده", "rejected": "رد شده"}.get(r["status"], "نامشخص")
        text += f"{status_icon} {r['amount']:,.0f} {symbol} ({r['created_at'][:10]})\n"

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=await back_to_menu())
