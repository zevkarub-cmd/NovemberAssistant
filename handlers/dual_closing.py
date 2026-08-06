from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import database


def duo_start_keyboard(session_id, employee_number):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Начать мои задачи",
                    callback_data=f"duostart_{session_id}_{employee_number}",
                )
            ]
        ]
    )


async def join_closing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if not database.employee_exists(telegram_id):
        await update.message.reply_text("Сначала пройдите регистрацию через /start.")
        return

    session = database.get_waiting_closing_session()

    if not session:
        await update.message.reply_text("Сейчас нет закрытия, ожидающего второго сотрудника.")
        return

    session_id, starter_id, _, _, _, _ = session

    if starter_id == telegram_id:
        await update.message.reply_text("Вы уже начали это закрытие как первый сотрудник.")
        return

    database.join_closing_session(session_id, telegram_id)

    starter_name = database.get_employee_name(starter_id)

    await update.message.reply_text(
        f"✅ Вы присоединились к закрытию вместе с {starter_name}.\n\n"
        "Нажмите кнопку ниже, чтобы начать свои задачи.",
        reply_markup=duo_start_keyboard(session_id, 2),
    )

    await context.bot.send_message(
        chat_id=starter_id,
        text=(
            "✅ Второй сотрудник присоединился к закрытию.\n\n"
            "Нажмите кнопку ниже, чтобы начать свои задачи."
        ),
        reply_markup=duo_start_keyboard(session_id, 1),
    )
