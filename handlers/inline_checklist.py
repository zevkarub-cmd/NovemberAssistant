from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CallbackQueryHandler, ContextTypes

import checklist_service
import database
from notifications import notify_closing_area
from roles import can_use_bot, has_barista_access

BAR_INVENTORY_PHOTO_ITEM = "📦 Фото остатков"

BAR_CLOSING_EXTRA_TEXT = """🎉 Чек-лист завершён.

Отправьте фотографии остатков
или напишите комментарий.

• Цитрусы (все)
• Молоко / альтернативное молоко / сливки / безлактозное молоко
• Драже / клюква / шишка / конфеты
• Газированная вода
• Чековая лента

Достаточно одного варианта: фото или комментарий.
После этого появится кнопка «✅ Готово»."""

BAR_CLOSING_EXTRA_STAGE = "bar_closing_extra"

BUTTON_TEXT_LIMIT = 64


def bar_inventory_photo_keyboard(step=0):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Готово",
                    callback_data=f"barphotos_done_{step}",
                )
            ]
        ]
    )


def closing_area_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💵 Касса",
                    callback_data="closearea_cash",
                )
            ],
            [
                InlineKeyboardButton(
                    "🍸 Бар",
                    callback_data="closearea_bar",
                )
            ],
        ]
    )


def _is_bar_inventory_photo_item(item):
    return item[2].strip() == BAR_INVENTORY_PHOTO_ITEM


def _truncate_button_text(text, limit=BUTTON_TEXT_LIMIT):
    text = " ".join(text.split())

    if len(text) <= limit:
        return text

    return text[: limit - 1] + "…"


def _progress_block(done, total):
    percent = int(round((done / total) * 100)) if total else 0

    return (
        "————————————\n"
        f"Выполнено: {done} / {total} ({percent}%)\n"
        "————————————"
    )


def _checklist_message(title, done, total):
    return f"{title}\n\n{_progress_block(done, total)}"


def _todo_items(items):
    return [item for item in items if not _is_bar_inventory_photo_item(item)]


def _todo_keyboard(prefix, items, checked):
    buttons = []

    for index, item in enumerate(items):
        mark = "☑" if index in checked else "☐"
        label = _truncate_button_text(f"{mark} {item[2]}")
        buttons.append(
            [
                InlineKeyboardButton(
                    label,
                    callback_data=f"{prefix}_{index}",
                )
            ]
        )

    return InlineKeyboardMarkup(buttons)


def _get_checked(context):
    return set(context.user_data.get("checklist_checked", []))


def _set_checked(context, checked):
    context.user_data["checklist_checked"] = sorted(checked)


EMPTY_INLINE_KEYBOARD = InlineKeyboardMarkup([])


async def _safe_edit_message(query, text, reply_markup=None):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as error:
        if "Message is not modified" not in str(error):
            raise


def _deactivate_checklist(context):
    """Prevent stale checklist buttons from re-entering the finish flow."""
    context.user_data.pop("checklist_prefix", None)
    context.user_data.pop("checklist_todo_items", None)
    context.user_data.pop("checklist_checked", None)


async def _show_bar_closing_extra_stage(query, context, step=0, reset_comment=True):
    context.user_data["photo_stage"] = BAR_CLOSING_EXTRA_STAGE
    context.user_data["bar_inventory_photo_step"] = step

    if reset_comment:
        context.user_data.pop("bar_closing_comment", None)

    _deactivate_checklist(context)

    await _safe_edit_message(
        query,
        BAR_CLOSING_EXTRA_TEXT,
        reply_markup=EMPTY_INLINE_KEYBOARD,
    )


async def _finish_closing_area(query, context, area):
    if area == "cash":
        context.user_data["photo_stage"] = "cash_closing_cash"
        _deactivate_checklist(context)

        await _safe_edit_message(
            query,
            "🎉 Чек-лист завершён.\n\n"
            "💵 Наличные:",
            reply_markup=EMPTY_INLINE_KEYBOARD,
        )
        return

    await _show_bar_closing_extra_stage(query, context, 0, reset_comment=True)


async def _finish_opening(query, context):
    context.user_data["photo_stage"] = "opening_cash"
    _deactivate_checklist(context)

    await _safe_edit_message(
        query,
        "🎉 Чек-лист завершён.\n\n"
        "💵 Введите сумму наличных в кассе на начало смены.\n\n"
        "Пример: 5000 или 5000.50",
        reply_markup=EMPTY_INLINE_KEYBOARD,
    )


async def _finish_handover(query, context):
    context.user_data["photo_stage"] = "handover_comment"
    _deactivate_checklist(context)

    await _safe_edit_message(
        query,
        "🎉 Чек-лист завершён.\n\n"
        "💬 Напишите комментарий к пересменке. Если комментариев нет — отправьте «-».",
        reply_markup=EMPTY_INLINE_KEYBOARD,
    )


async def _render_checklist(message_or_query, context, *, edit=False):
    title = context.user_data["checklist_title"]
    prefix = context.user_data["checklist_prefix"]
    items = context.user_data["checklist_todo_items"]
    checked = _get_checked(context)
    text = _checklist_message(title, len(checked), len(items))
    keyboard = _todo_keyboard(prefix, items, checked)

    if edit:
        await _safe_edit_message(message_or_query, text, reply_markup=keyboard)
        return

    await message_or_query.reply_text(text, reply_markup=keyboard)


async def _start_todo_checklist(
    update,
    context,
    checklist_type,
    title,
    prefix,
    assignee=None,
):
    items = checklist_service.get_items(checklist_type, assignee=assignee)

    if not items:
        await update.message.reply_text(
            f"Чек-лист «{title}» пока пуст. Владелец может заполнить его в управлении чек-листами."
        )
        return

    todo_items = _todo_items(items)

    context.user_data["checklist_type"] = checklist_type
    context.user_data["checklist_title"] = title
    context.user_data["checklist_prefix"] = prefix
    context.user_data["checklist_items"] = [item[0] for item in items]
    context.user_data["checklist_todo_items"] = todo_items
    context.user_data["checklist_checked"] = []

    if not todo_items:
        if prefix == "close" and any(_is_bar_inventory_photo_item(item) for item in items):
            context.user_data["photo_stage"] = BAR_CLOSING_EXTRA_STAGE
            context.user_data["bar_inventory_photo_step"] = 0
            _deactivate_checklist(context)
            await update.message.reply_text(BAR_CLOSING_EXTRA_TEXT)
            return

        await update.message.reply_text(
            f"Чек-лист «{title}» пока пуст. Владелец может заполнить его в управлении чек-листами."
        )
        return

    await _render_checklist(update.message, context, edit=False)


async def _start_todo_checklist_from_query(
    query,
    context,
    checklist_type,
    title,
    prefix,
    assignee=None,
):
    items = checklist_service.get_items(checklist_type, assignee=assignee)

    if not items:
        await query.edit_message_text(
            f"{title}\n\n"
            "Чек-лист пока пуст. Пришлите пункты, и я добавлю их под эту кнопку."
        )
        return

    todo_items = _todo_items(items)

    context.user_data["checklist_type"] = checklist_type
    context.user_data["checklist_title"] = title
    context.user_data["checklist_prefix"] = prefix
    context.user_data["checklist_items"] = [item[0] for item in items]
    context.user_data["checklist_todo_items"] = todo_items
    context.user_data["checklist_checked"] = []

    if not todo_items:
        if prefix == "close" and any(_is_bar_inventory_photo_item(item) for item in items):
            await _show_bar_closing_extra_stage(query, context, 0)
            return

        await query.edit_message_text(
            f"{title}\n\n"
            "Чек-лист пока пуст. Пришлите пункты, и я добавлю их под эту кнопку."
        )
        return

    await _render_checklist(query, context, edit=True)


async def _toggle_checklist(update, context, prefix):
    query = update.callback_query
    role = database.get_employee_role(query.from_user.id)

    if not can_use_bot(role) or not has_barista_access(role):
        await query.answer("Нет доступа.", show_alert=True)
        return

    stage = context.user_data.get("photo_stage")
    if stage in {
        BAR_CLOSING_EXTRA_STAGE,
        "cash_closing_cash",
        "cash_closing_card",
        "cash_closing_refunds",
        "cash_closing_comment",
        "opening_cash",
        "opening_comment",
        "handover_comment",
    }:
        await query.answer(
            "Чек-лист уже завершён. Продолжите ввод ниже.",
            show_alert=True,
        )
        return

    if context.user_data.get("checklist_prefix") != prefix:
        await query.answer("Этот чек-лист уже неактивен. Откройте его заново.", show_alert=True)
        return

    await query.answer()

    items = context.user_data.get("checklist_todo_items") or []

    if not items:
        return

    try:
        index = int(query.data.split("_")[1])
    except (IndexError, ValueError):
        return

    if index < 0 or index >= len(items):
        return

    checked = _get_checked(context)

    if index in checked:
        checked.remove(index)
    else:
        checked.add(index)

    _set_checked(context, checked)

    if len(checked) >= len(items):
        if prefix == "open":
            await _finish_opening(query, context)
        elif prefix == "close":
            area = context.user_data.get("closing_area", "cash")
            await _finish_closing_area(query, context, area)
        elif prefix == "hand":
            await _finish_handover(query, context)
        return

    await _render_checklist(query, context, edit=True)


async def start_opening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if not database.employee_exists(telegram_id):
        await update.message.reply_text("Сначала пройдите регистрацию через /start.")
        return

    role = database.get_employee_role(telegram_id)

    if not can_use_bot(role) or not has_barista_access(role):
        return

    context.user_data.clear()
    context.user_data["mode"] = "opening"

    await _start_todo_checklist(
        update,
        context,
        checklist_service.CHECKLIST_OPENING,
        "☀️ Открытие смены",
        "open",
    )


async def start_closing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if not database.employee_exists(telegram_id):
        await update.message.reply_text("Сначала пройдите регистрацию через /start.")
        return

    role = database.get_employee_role(telegram_id)

    if not can_use_bot(role) or not has_barista_access(role):
        return

    context.user_data.clear()

    await update.message.reply_text(
        "🌙 Закрытие смены\n\nВыберите, что закрываете:",
        reply_markup=closing_area_keyboard(),
    )


async def start_handover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if not database.employee_exists(telegram_id):
        await update.message.reply_text("Сначала пройдите регистрацию через /start.")
        return

    role = database.get_employee_role(telegram_id)

    if not can_use_bot(role) or not has_barista_access(role):
        return

    context.user_data.clear()
    context.user_data["mode"] = "handover"

    await _start_todo_checklist(
        update,
        context,
        checklist_service.CHECKLIST_HANDOVER,
        "🔄 Пересменка",
        "hand",
    )


async def closing_area_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    role = database.get_employee_role(query.from_user.id)

    if not can_use_bot(role) or not has_barista_access(role):
        await query.answer("Нет доступа.", show_alert=True)
        return

    await query.answer()

    area = query.data.split("_")[1]
    assignee = (
        checklist_service.ASSIGNEE_FIRST
        if area == "cash"
        else checklist_service.ASSIGNEE_SECOND
    )
    title = "🌙 Закрытие кассы" if area == "cash" else "🌙 Закрытие бара"

    context.user_data.clear()
    context.user_data["mode"] = "closing"
    context.user_data["closing_area"] = area
    context.user_data["closing_assignee"] = assignee

    await _start_todo_checklist_from_query(
        query,
        context,
        checklist_service.CHECKLIST_CLOSING,
        title,
        "close",
        assignee=assignee,
    )


async def opening_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _toggle_checklist(update, context, "open")


async def closing_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _toggle_checklist(update, context, "close")


async def handover_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _toggle_checklist(update, context, "hand")


async def bar_inventory_photo_done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    telegram_id = query.from_user.id
    role = database.get_employee_role(telegram_id)

    if not can_use_bot(role) or not has_barista_access(role):
        await query.answer("Нет доступа.", show_alert=True)
        return

    photos = context.user_data.get("bar_inventory_photo_ids", [])
    comment = (context.user_data.get("bar_closing_comment") or "").strip()

    if not photos and not comment:
        await query.answer(
            "Сначала отправьте фото или напишите комментарий.",
            show_alert=True,
        )
        return

    await query.answer()

    closing_id = database.save_closing_now(
        telegram_id,
        comment=comment,
        mode="bar",
    )

    await notify_closing_area(
        context,
        telegram_id,
        "bar",
        comment=comment,
        photos=photos,
    )

    context.user_data.clear()

    comment_text = comment if comment else "—"
    photos_text = str(len(photos)) if photos else "0"

    await _safe_edit_message(
        query,
        "✅ Закрытие бара сохранено.\n\n"
        f"📷 Фото: {photos_text}\n"
        f"💬 Комментарий: {comment_text}\n\n"
        f"Номер записи: {closing_id}",
        reply_markup=EMPTY_INLINE_KEYBOARD,
    )


opening_handler = CallbackQueryHandler(opening_callback, pattern=r"^open_\d+$")
closing_handler = CallbackQueryHandler(closing_callback, pattern=r"^close_\d+$")
handover_handler = CallbackQueryHandler(handover_callback, pattern=r"^hand_\d+$")
closing_area_handler = CallbackQueryHandler(
    closing_area_callback,
    pattern=r"^closearea_",
)
bar_inventory_photo_done_handler = CallbackQueryHandler(
    bar_inventory_photo_done_callback,
    pattern=r"^barphotos_done_",
)
