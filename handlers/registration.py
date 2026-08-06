from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import database
from keyboards import get_main_keyboard
from roles import ROLE_VERIFICATION, can_use_bot, role_label

ASK_NAME = 1


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if database.employee_exists(telegram_id):
        name = database.get_employee_name(telegram_id)
        role = database.get_employee_role(telegram_id)

        if not can_use_bot(role):
            await update.message.reply_text(
                f"Здравствуйте, {name}.\n\n"
                f"Ваша текущая роль: {role_label(role)}.\n"
                "Доступ к боту откроет владелец или управляющий."
            )
            return ConversationHandler.END

        await update.message.reply_text(
            f"С возвращением, {name}! ☕",
            reply_markup=get_main_keyboard(role),
        )

        return ConversationHandler.END

    await update.message.reply_text(
        "👋 Добро пожаловать в November Assistant!\n\nВведите своё имя:"
    )

    return ASK_NAME


async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text("Имя не может быть пустым. Введите своё имя:")
        return ASK_NAME

    database.add_employee(telegram_id, name)
    role = database.get_employee_role(telegram_id)

    if role == ROLE_VERIFICATION or not can_use_bot(role):
        await update.message.reply_text(
            f"Рад знакомству, {name}!\n\n"
            f"Ваша текущая роль: {role_label(role)}.\n"
            "Доступ к боту откроет владелец или управляющий после проверки.",
            reply_markup=get_main_keyboard(role),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        f"Рад знакомству, {name}! ☕",
        reply_markup=get_main_keyboard(role),
    )

    return ConversationHandler.END


registration_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", register),
        MessageHandler(filters.TEXT & filters.Regex("^/start$"), register),
    ],
    states={
        ASK_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_name),
        ],
    },
    fallbacks=[],
)
