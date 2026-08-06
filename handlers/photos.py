from telegram import Update
from telegram.ext import ContextTypes

import database
from handlers.inline_checklist import (
    BAR_CLOSING_EXTRA_STAGE,
    bar_inventory_photo_keyboard,
)
from roles import can_use_bot, has_barista_access


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    if context.user_data.get("photo_stage") != BAR_CLOSING_EXTRA_STAGE:
        return

    telegram_id = update.effective_user.id
    role = database.get_employee_role(telegram_id)

    if not can_use_bot(role) or not has_barista_access(role):
        return

    photo = update.message.photo[-1].file_id

    database.save_closing_inventory_photo(telegram_id, photo)
    context.user_data.setdefault("bar_inventory_photo_ids", []).append(photo)
    step = context.user_data.get("bar_inventory_photo_step", 0)

    caption = (update.message.caption or "").strip()
    if caption and caption != "-":
        context.user_data["bar_closing_comment"] = caption

    await update.message.reply_text(
        "✅ Фото сохранено.\n\n"
        "Можно отправить ещё фото, дописать комментарий "
        "или нажать «✅ Готово».",
        reply_markup=bar_inventory_photo_keyboard(step),
    )
