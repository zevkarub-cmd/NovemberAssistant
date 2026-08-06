from telegram import Update
from telegram.ext import ContextTypes

import database
from keyboards import get_main_keyboard
from notifications import notify_accounting_opening, notify_opening
from roles import can_use_bot, has_barista_access
from utils import format_amount, parse_amount

OPENING_TEXT_STAGES = {
    "opening_cash",
    "opening_comment",
}


async def opening_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stage = context.user_data.get("photo_stage")

    if stage not in OPENING_TEXT_STAGES:
        return

    text = update.message.text.strip()
    telegram_id = update.effective_user.id
    role = database.get_employee_role(telegram_id)

    if not can_use_bot(role) or not has_barista_access(role):
        return

    if stage == "opening_cash":
        try:
            amount = parse_amount(text)
        except ValueError:
            await update.message.reply_text(
                "❌ Введите корректное число.\n\n"
                "Пример: 5000 или 5000.50"
            )
            return

        context.user_data["opening_cash"] = amount
        context.user_data["photo_stage"] = "opening_comment"

        await update.message.reply_text(
            "💬 Напишите комментарий к открытию смены.\n\n"
            "Если комментариев нет — отправьте «-»."
        )
        return

    if stage == "opening_comment":
        comment = "" if text == "-" else text
        opening_cash = context.user_data.get("opening_cash", 0)

        opening_id = database.save_opening_now(
            telegram_id,
            comment,
            opening_cash,
        )

        await notify_accounting_opening(context, telegram_id, opening_cash)
        await notify_opening(context, telegram_id, opening_id)

        context.user_data.clear()

        comment_text = comment if comment else "—"

        await update.message.reply_text(
            "🎉 Открытие смены завершено!\n\n"
            f"💵 Наличные в кассе: {format_amount(opening_cash)} ₽\n"
            f"💬 Комментарий: {comment_text}\n\n"
            "Желаю хорошей смены ☕",
            reply_markup=get_main_keyboard(role),
        )
