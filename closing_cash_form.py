from telegram import Update
from telegram.ext import ContextTypes

import database
from handlers.inline_checklist import (
    BAR_CLOSING_EXTRA_STAGE,
    bar_inventory_photo_keyboard,
)
from keyboards import get_main_keyboard
from notifications import notify_accounting_closing, notify_closing_area
from roles import can_use_bot, has_barista_access
from utils import format_amount, parse_amount

CASH_CLOSING_STAGES = {
    "cash_closing_cash",
    "cash_closing_card",
    "cash_closing_refunds",
    "cash_closing_comment",
    BAR_CLOSING_EXTRA_STAGE,
}


async def closing_cash_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stage = context.user_data.get("photo_stage")

    if stage not in CASH_CLOSING_STAGES:
        return

    text = update.message.text.strip()
    telegram_id = update.effective_user.id
    role = database.get_employee_role(telegram_id)

    if not can_use_bot(role) or not has_barista_access(role):
        return

    if stage == BAR_CLOSING_EXTRA_STAGE:
        comment = "" if text == "-" else text
        photos = context.user_data.get("bar_inventory_photo_ids", [])

        if not comment and not photos:
            await update.message.reply_text(
                "❌ Комментарий пустой.\n\n"
                "Напишите текст или отправьте фото."
            )
            return

        context.user_data["bar_closing_comment"] = comment
        step = context.user_data.get("bar_inventory_photo_step", 0)

        await update.message.reply_text(
            "✅ Комментарий сохранён.\n\n"
            "Можно отправить фото или нажать «✅ Готово».",
            reply_markup=bar_inventory_photo_keyboard(step),
        )
        return

    if stage == "cash_closing_comment":
        comment = "" if text == "-" else text
        cash_revenue = context.user_data.get("cash_revenue", 0)
        card_revenue = context.user_data.get("card_revenue", 0)
        refunds_amount = context.user_data.get("refunds_amount", 0)

        closing_id = database.save_closing_now(
            telegram_id,
            comment=comment,
            total_revenue=cash_revenue + card_revenue,
            card_revenue=card_revenue,
            cash_revenue=cash_revenue,
            mode="cash",
            refunds_amount=refunds_amount,
        )

        extra_text = (
            f"💵 Наличные: {format_amount(cash_revenue)} ₽\n"
            f"💳 Безналичные: {format_amount(card_revenue)} ₽\n"
            f"↩️ Возвраты/отмены: {format_amount(refunds_amount)} ₽"
        )

        await notify_accounting_closing(
            context,
            telegram_id,
            cash_revenue,
            card_revenue,
            refunds_amount,
        )
        await notify_closing_area(
            context,
            telegram_id,
            "cash",
            comment=comment,
            extra_text=extra_text,
        )

        context.user_data.clear()

        comment_text = comment if comment else "—"

        await update.message.reply_text(
            "✅ Закрытие кассы сохранено.\n\n"
            f"💵 Наличные: {format_amount(cash_revenue)} ₽\n"
            f"💳 Безналичные: {format_amount(card_revenue)} ₽\n"
            f"↩️ Возвраты/отмены: {format_amount(refunds_amount)} ₽\n"
            f"💬 Комментарий: {comment_text}\n\n"
            f"Номер записи: {closing_id}",
            reply_markup=get_main_keyboard(role),
        )
        return

    try:
        amount = parse_amount(text)
    except ValueError:
        await update.message.reply_text(
            "❌ Введите корректное число.\n\n"
            "Пример: 5000 или 5000.50"
        )
        return

    if stage == "cash_closing_cash":
        context.user_data["cash_revenue"] = amount
        context.user_data["photo_stage"] = "cash_closing_card"

        await update.message.reply_text("💳 Безналичные:")
        return

    if stage == "cash_closing_card":
        context.user_data["card_revenue"] = amount
        context.user_data["photo_stage"] = "cash_closing_refunds"

        await update.message.reply_text("↩️ Возвраты/отмены:")
        return

    if stage == "cash_closing_refunds":
        context.user_data["refunds_amount"] = amount
        context.user_data["photo_stage"] = "cash_closing_comment"

        await update.message.reply_text(
            "💬 Напишите комментарий к закрытию кассы.\n\n"
            "Если комментариев нет — отправьте «-»."
        )
        return
