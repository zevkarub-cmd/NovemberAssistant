from telegram import Update
from telegram.ext import ContextTypes

import database
from keyboards import get_main_keyboard
from notifications import notify_closing
from utils import format_amount, parse_amount

CLOSING_TEXT_STAGES = {
    "closing_comment",
    "closing_total",
    "closing_card",
    "closing_cash",
    "closing_change",
    "closing_largest",
}


async def closing_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stage = context.user_data.get("photo_stage")

    if stage not in CLOSING_TEXT_STAGES:
        return

    text = update.message.text.strip()
    telegram_id = update.effective_user.id
    role = database.get_employee_role(telegram_id)

    if stage == "closing_comment":
        context.user_data["closing_comment"] = "" if text == "-" else text
        context.user_data["photo_stage"] = "closing_total"

        await update.message.reply_text(
            "💰 Введите общую выручку за смену.\n\n"
            "Пример: 12500 или 12500.50"
        )
        return

    try:
        amount = parse_amount(text)
    except ValueError:
        await update.message.reply_text(
            "❌ Введите корректное число.\n\n"
            "Пример: 12500 или 12500.50"
        )
        return

    if stage == "closing_total":
        context.user_data["total_revenue"] = amount
        context.user_data["photo_stage"] = "closing_card"

        await update.message.reply_text("💳 Введите выручку по карте.")
        return

    if stage == "closing_card":
        context.user_data["card_revenue"] = amount
        context.user_data["photo_stage"] = "closing_cash"

        await update.message.reply_text("💵 Введите выручку наличными.")
        return

    if stage == "closing_cash":
        context.user_data["cash_revenue"] = amount
        context.user_data["photo_stage"] = "closing_change"

        await update.message.reply_text("🪙 Введите сумму на размен.")
        return

    if stage == "closing_change":
        context.user_data["change_amount"] = amount
        context.user_data["photo_stage"] = "closing_largest"

        await update.message.reply_text("🏆 Введите сумму самого большого чека.")
        return

    if stage == "closing_largest":
        context.user_data["largest_check"] = amount

        closing_mode = context.user_data.get("closing_mode", "solo")
        session_id = context.user_data.get("closing_session_id")
        telegram_id_2 = None

        if closing_mode == "duo" and session_id:
            session = database.get_closing_session(session_id)

            if session:
                _, starter_id, partner_id, _, _, _ = session
                telegram_id = starter_id
                telegram_id_2 = partner_id

        closing_id = database.save_closing_now(
            telegram_id,
            context.user_data.get("closing_comment", ""),
            context.user_data.get("total_revenue", 0),
            context.user_data.get("card_revenue", 0),
            context.user_data.get("cash_revenue", 0),
            context.user_data.get("change_amount", 0),
            amount,
            telegram_id_2,
            closing_mode,
        )

        if session_id:
            database.complete_closing_session(session_id)

        await notify_closing(context, update.effective_user.id, closing_id)

        total = context.user_data.get("total_revenue", 0)
        card = context.user_data.get("card_revenue", 0)
        cash = context.user_data.get("cash_revenue", 0)
        change = context.user_data.get("change_amount", 0)
        largest = amount

        context.user_data.clear()

        await update.message.reply_text(
            "🌙 Закрытие смены завершено!\n\n"
            f"💰 Общая выручка: {format_amount(total)} ₽\n"
            f"💳 По карте: {format_amount(card)} ₽\n"
            f"💵 Наличными: {format_amount(cash)} ₽\n"
            f"🪙 На размен: {format_amount(change)} ₽\n"
            f"🏆 Самый большой чек: {format_amount(largest)} ₽\n\n"
            "Спасибо за работу ☕",
            reply_markup=get_main_keyboard(role),
        )
