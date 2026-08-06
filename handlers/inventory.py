from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

import database
from keyboards import get_main_keyboard
from notifications import notify_inventory
from roles import can_use_bot, has_barista_access


async def start_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if not database.employee_exists(telegram_id):
        await update.message.reply_text("Сначала пройдите регистрацию через /start.")
        return

    role = database.get_employee_role(telegram_id)

    if not can_use_bot(role) or not has_barista_access(role):
        return

    context.user_data.clear()

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "❌ Закончилось",
                    callback_data="inv_out",
                )
            ],
            [
                InlineKeyboardButton(
                    "⚠️ Заканчивается",
                    callback_data="inv_low",
                )
            ],
        ]
    )

    await update.message.reply_text(
        "📦 Остатки\n\nВыберите тип сообщения:",
        reply_markup=keyboard,
    )


async def inventory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    role = database.get_employee_role(query.from_user.id)

    if not can_use_bot(role) or not has_barista_access(role):
        await query.answer("Нет доступа.", show_alert=True)
        return

    await query.answer()

    status_map = {
        "inv_out": "out",
        "inv_low": "low",
    }

    status = status_map.get(query.data)

    if not status:
        return

    context.user_data.clear()
    context.user_data["photo_stage"] = "inventory_message"
    context.user_data["inventory_status"] = status

    status_label = "закончилось" if status == "out" else "заканчивается"

    await query.edit_message_text(
        "📝 Напишите сообщение об остатках.\n\n"
        f"Например: «{status_label.capitalize()} молоко.»"
    )


async def inventory_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("photo_stage") != "inventory_message":
        return

    role = database.get_employee_role(update.effective_user.id)

    if not can_use_bot(role) or not has_barista_access(role):
        return

    message = update.message.text.strip()

    if not message:
        await update.message.reply_text("❌ Сообщение не может быть пустым.")
        return

    telegram_id = update.effective_user.id
    status = context.user_data.get("inventory_status", "low")

    database.save_inventory_message(telegram_id, status, message)
    await notify_inventory(context, telegram_id, status, message)

    context.user_data.clear()

    await update.message.reply_text(
        "✅ Сообщение об остатках отправлено.",
        reply_markup=get_main_keyboard(role),
    )


inventory_callback_handler = CallbackQueryHandler(
    inventory_callback,
    pattern=r"^inv_(out|low)$",
)
