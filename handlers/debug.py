from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from config import OWNER_TELEGRAM_ID


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or user.id != OWNER_TELEGRAM_ID:
        return

    thread_id = getattr(message, "message_thread_id", None)
    thread_text = str(thread_id) if thread_id is not None else "Нет"
    is_topic = bool(getattr(message, "is_topic_message", False) or thread_id is not None)
    topic_text = "Да" if is_topic else "Нет"

    text = (
        "====================\n\n"
        "DEBUG\n\n"
        "Chat ID:\n"
        f"{chat.id}\n\n"
        "Thread ID:\n"
        f"{thread_text}\n\n"
        "User ID:\n"
        f"{user.id}\n\n"
        "Chat type:\n"
        f"{chat.type}\n\n"
        "Topic:\n"
        f"{topic_text}\n\n"
        "===================="
    )

    await message.reply_text(text)


debug_handler = CommandHandler("debug", debug_command)
