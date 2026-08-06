from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import database
from keyboards import get_main_keyboard
from roles import can_broadcast, can_use_bot

BROADCAST_MENU_BUTTON = "📢 Сообщение всем"


async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = database.get_employee_role(update.effective_user.id)

    if not can_use_bot(role):
        return

    if not can_broadcast(role):
        await update.message.reply_text("У вас нет доступа к массовой рассылке.")
        return

    context.user_data.clear()
    context.user_data["photo_stage"] = "broadcast_message"

    await update.message.reply_text(
        "📢 Сообщение всем\n\n"
        "Напишите текст сообщения, которое нужно отправить сотрудникам."
    )


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("photo_stage") != "broadcast_message":
        return

    text = update.message.text.strip()

    # The same update that starts the flow also reaches this handler.
    # Ignore the menu button itself so the bot waits for real text.
    if text == BROADCAST_MENU_BUTTON:
        return

    role = database.get_employee_role(update.effective_user.id)

    if not can_use_bot(role) or not can_broadcast(role):
        context.user_data.clear()
        return

    if not text:
        await update.message.reply_text("❌ Сообщение не может быть пустым.")
        return

    recipients = database.get_broadcast_recipients()
    sent = 0

    for recipient_id in recipients:
        try:
            await context.bot.send_message(
                chat_id=recipient_id,
                text=f"📢 Сообщение от владельца:\n\n{text}",
            )
            sent += 1
        except TelegramError:
            continue

    context.user_data.clear()

    await update.message.reply_text(
        f"✅ Сообщение отправлено: {sent} из {len(recipients)}.",
        reply_markup=get_main_keyboard(role),
    )
