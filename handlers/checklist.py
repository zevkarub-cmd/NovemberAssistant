from telegram import Update
from telegram.ext import ContextTypes

import database


async def open_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = update.effective_user.id

    date, time = database.get_current_datetime_strings()

    database.save_opening(
        telegram_id,
        date,
        time,
    )

    await update.message.reply_text(
f"""☀️ Открытие смены

Дата: {date}
Время: {time}

☐ Включить свет

☐ Включить музыку

☐ Проверить кофемашину

☐ Проверить холодильники

☐ Проверить витрину

Удачной смены! ☕"""
    )