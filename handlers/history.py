from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from datetime import datetime

import database
from roles import can_use_bot, can_view_history
from utils import format_amount


def _has_history_access(telegram_id):
    role = database.get_employee_role(telegram_id)
    return can_use_bot(role) and can_view_history(role)


def _sort_dates(dates):
    def parse_date(date):
        try:
            return datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            return datetime.min

    return sorted(dates, key=parse_date, reverse=True)


def _history_dates_keyboard(history_type, dates):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    date,
                    callback_data=f"history_date_{history_type}_{date}",
                )
            ]
            for date in _sort_dates(dates)
        ]
        + [
            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data="history_back",
                )
            ]
        ]
    )


def _history_type_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "☀️ Открытия",
                    callback_data="history_openings",
                )
            ],
            [
                InlineKeyboardButton(
                    "🌙 Закрытия",
                    callback_data="history_closings",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔄 Пересменки",
                    callback_data="history_handovers",
                )
            ],
        ]
    )


async def _show_history_dates(query, history_type, title, rows, date_index):
    if not rows:
        await query.edit_message_text(f"{title}\n\nИстория пока пустая.")
        return

    dates = {row[date_index] for row in rows}

    await query.edit_message_text(
        f"{title}\n\nВыберите дату:",
        reply_markup=_history_dates_keyboard(history_type, dates),
    )


async def openings_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _has_history_access(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к истории открытий.")
        return

    await send_openings_history(update.message)


async def send_openings_history(message, selected_date=None):
    openings = database.get_openings_full()

    if selected_date:
        openings = [row for row in openings if row[2] == selected_date]

    if not openings:
        await message.reply_text("История открытий пока пустая.")
        return

    for _, _, date, time, name, opening_cash, comment in openings:
        comment_text = comment if comment else "—"

        await message.reply_text(
            f"👤 {name}\n"
            f"📅 {date}\n"
            f"🕒 {time}\n"
            f"💵 Наличные: {format_amount(opening_cash)} ₽\n"
            f"💬 Комментарий: {comment_text}"
        )


async def closings_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _has_history_access(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к истории закрытий.")
        return

    await send_closings_history(update.message)


async def send_closings_history(message, selected_date=None):
    closings = database.get_closings_full()

    if selected_date:
        closings = [row for row in closings if row[3] == selected_date]

    if not closings:
        await message.reply_text("История закрытий пока пустая.")
        return

    for (
        _,
        _,
        second_id,
        date,
        time,
        first_name,
        second_name,
        total_revenue,
        card_revenue,
        cash_revenue,
        change_amount,
        largest_check,
        comment,
        mode,
        cashbox_amount,
        refunds_amount,
    ) in closings:
        comment_text = comment if comment else "—"
        employees_text = f"👤 Сотрудник: {first_name}"
        mode_text = ""

        if mode == "duo" and second_id:
            employees_text = f"👤 Сотрудник 1: {first_name}\n👤 Сотрудник 2: {second_name}"

        if mode == "cash":
            mode_text = "📌 Раздел: Касса\n"
        elif mode == "bar":
            mode_text = "📌 Раздел: Бар\n"

        if mode == "cash":
            await message.reply_text(
                f"{employees_text}\n"
                f"{mode_text}"
                f"📅 {date}\n"
                f"🕒 {time}\n"
                f"💵 Наличные: {format_amount(cash_revenue)} ₽\n"
                f"💳 Безналичные: {format_amount(card_revenue)} ₽\n"
                f"↩️ Возвраты/отмены: {format_amount(refunds_amount)} ₽\n"
                f"💬 Комментарий: {comment_text}"
            )
        elif mode == "bar":
            await message.reply_text(
                f"{employees_text}\n"
                f"{mode_text}"
                f"📅 {date}\n"
                f"🕒 {time}\n"
                f"💬 Комментарий: {comment_text}"
            )
        else:
            await message.reply_text(
                f"{employees_text}\n"
                f"📅 {date}\n"
                f"🕒 {time}\n"
                f"💰 Общая выручка: {format_amount(total_revenue)} ₽\n"
                f"💳 По карте: {format_amount(card_revenue)} ₽\n"
                f"💵 Наличными: {format_amount(cash_revenue)} ₽\n"
                f"🪙 На размен: {format_amount(change_amount)} ₽\n"
                f"🏆 Самый большой чек: {format_amount(largest_check)} ₽\n"
                f"💬 Комментарий: {comment_text}"
            )


async def handovers_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _has_history_access(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к истории пересменок.")
        return

    await send_handovers_history(update.message)


async def send_handovers_history(message, selected_date=None):
    handovers = database.get_handovers_full()

    if selected_date:
        handovers = [row for row in handovers if row[2] == selected_date]

    if not handovers:
        await message.reply_text("История пересменок пока пустая.")
        return

    for _, _, date, time, name, comment, status in handovers:
        comment_text = comment if comment else "—"

        await message.reply_text(
            f"👤 Сотрудник: {name}\n"
            f"📅 {date}\n"
            f"🕒 {time}\n"
            f"✅ Статус: {status}\n"
            f"💬 Комментарий: {comment_text}"
        )


async def start_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = database.get_employee_role(update.effective_user.id)

    if not can_use_bot(role):
        return

    if not can_view_history(role):
        await update.message.reply_text("У вас нет доступа к истории.")
        return

    context.user_data.clear()

    await update.message.reply_text(
        "📊 История\n\nВыберите раздел:",
        reply_markup=_history_type_keyboard(),
    )


async def history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if not _has_history_access(query.from_user.id):
        await query.answer("Нет доступа.", show_alert=True)
        return

    await query.answer()

    if query.data == "history_back":
        await query.edit_message_text(
            "📊 История\n\nВыберите раздел:",
            reply_markup=_history_type_keyboard(),
        )
        return

    if query.data == "history_openings":
        await _show_history_dates(
            query,
            "openings",
            "📊 История открытий",
            database.get_openings_full(),
            2,
        )
        return

    if query.data == "history_closings":
        await _show_history_dates(
            query,
            "closings",
            "📊 История закрытий",
            database.get_closings_full(),
            3,
        )
        return

    if query.data == "history_handovers":
        await _show_history_dates(
            query,
            "handovers",
            "📊 История пересменок",
            database.get_handovers_full(),
            2,
        )
        return

    if query.data.startswith("history_date_"):
        _, _, history_type, selected_date = query.data.split("_", 3)

        await query.edit_message_text(f"📊 История за {selected_date}")

        if history_type == "openings":
            await send_openings_history(query.message, selected_date)
        elif history_type == "closings":
            await send_closings_history(query.message, selected_date)
        elif history_type == "handovers":
            await send_handovers_history(query.message, selected_date)

        return

    await query.message.reply_text("Неизвестный раздел истории.")


history_handler = CallbackQueryHandler(
    history_callback,
    pattern=r"^history_",
)
