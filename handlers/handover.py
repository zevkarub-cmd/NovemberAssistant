from telegram import Update
from telegram.ext import ContextTypes

import database
from keyboards import get_main_keyboard
from notifications import notify_handover
from roles import can_use_bot, has_barista_access


async def handover_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("photo_stage") != "handover_comment":
        return

    telegram_id = update.effective_user.id
    role = database.get_employee_role(telegram_id)

    if not can_use_bot(role) or not has_barista_access(role):
        return

    text = update.message.text.strip()
    comment = "" if text == "-" else text

    handover_id = database.save_handover(
        telegram_id,
        comment,
        "completed",
    )

    await notify_handover(context, telegram_id, handover_id)

    context.user_data.clear()

    await update.message.reply_text(
        "✅ Пересменка сохранена.",
        reply_markup=get_main_keyboard(role),
    )
