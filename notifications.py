from telegram.error import TelegramError

from config import ACCOUNTING_CHAT_ID, ACCOUNTING_MESSAGE_THREAD_ID
import database
from utils import format_amount


async def _safe_send_message(context, chat_id, text, target, message_thread_id=None):
    kwargs = {}

    if message_thread_id is not None:
        kwargs["message_thread_id"] = message_thread_id

    try:
        await context.bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except TelegramError as error:
        print(f"Не удалось отправить сообщение ({target}): {error}")


async def _safe_send_photo(context, chat_id, photo_id, target):
    try:
        await context.bot.send_photo(chat_id=chat_id, photo=photo_id)
    except TelegramError as error:
        print(f"Не удалось отправить фото ({target}): {error}")


async def _send_to_recipients(context, sender_id, text, photos=None):
    photos = photos or []

    for recipient_id in database.get_notification_recipients():
        if recipient_id == sender_id:
            continue

        await _safe_send_message(context, recipient_id, text, "уведомления")

        for photo_id in photos:
            await _safe_send_photo(context, recipient_id, photo_id, "уведомления")


async def _send_to_accounting(context, text):
    if not ACCOUNTING_CHAT_ID:
        return

    await _safe_send_message(
        context,
        ACCOUNTING_CHAT_ID,
        text,
        "бухгалтерия",
        message_thread_id=ACCOUNTING_MESSAGE_THREAD_ID,
    )


async def notify_accounting_opening(context, telegram_id, opening_cash):
    name = database.get_employee_name(telegram_id)

    text = (
        "Деньги на начало смены\n\n"
        f"Бариста: {name}\n\n"
        "Наличные:\n"
        f"{format_amount(opening_cash)} ₽"
    )

    await _send_to_accounting(context, text)


async def notify_accounting_closing(
    context,
    telegram_id,
    cash_revenue,
    card_revenue,
    refunds_amount,
):
    name = database.get_employee_name(telegram_id)

    text = (
        "Деньги на конец смены\n\n"
        f"Бариста: {name}\n\n"
        "Наличные:\n"
        f"{format_amount(cash_revenue)} ₽\n\n"
        "Безналичные:\n"
        f"{format_amount(card_revenue)} ₽\n\n"
        "Возвраты/отмены:\n"
        f"{format_amount(refunds_amount)} ₽"
    )

    await _send_to_accounting(context, text)


async def notify_opening(context, telegram_id, opening_id):
    opening = database.get_opening_by_id(opening_id)

    if not opening:
        return

    _, _, date, time, comment, opening_cash = opening
    name = database.get_employee_name(telegram_id)
    comment_text = comment if comment else "—"

    text = (
        "☀️ Выполнен чек-лист утро\n\n"
        f"👤 Сотрудник: {name}\n"
        f"📅 Дата: {date}\n"
        f"🕒 Время: {time}\n"
        f"💵 Наличные в кассе: {format_amount(opening_cash)} ₽\n"
        f"💬 Комментарий: {comment_text}"
    )

    await _send_to_recipients(context, telegram_id, text)


async def notify_closing(context, telegram_id, closing_id):
    closing = database.get_closing_by_id(closing_id)

    if not closing:
        return

    (
        _,
        first_id,
        second_id,
        date,
        time,
        comment,
        mode,
        total_revenue,
        card_revenue,
        cash_revenue,
        change_amount,
        largest_check,
    ) = closing

    first_name = database.get_employee_name(first_id)
    second_name = database.get_employee_name(second_id) if second_id else "—"
    comment_text = comment if comment else "—"

    employee_text = f"👤 Сотрудник: {first_name}"

    if mode == "duo" and second_id:
        employee_text = f"👤 Сотрудник 1: {first_name}\n👤 Сотрудник 2: {second_name}"

    text = (
        "🌙 Закрытие смены\n\n"
        f"{employee_text}\n"
        f"📅 Дата: {date}\n"
        f"🕒 Время: {time}\n"
        f"💰 Общая выручка: {format_amount(total_revenue)} ₽\n"
        f"💳 По карте: {format_amount(card_revenue)} ₽\n"
        f"💵 Наличными: {format_amount(cash_revenue)} ₽\n"
        f"🪙 На размен: {format_amount(change_amount)} ₽\n"
        f"🏆 Самый большой чек: {format_amount(largest_check)} ₽\n"
        f"💬 Комментарий: {comment_text}"
    )

    await _send_to_recipients(context, telegram_id, text)


async def notify_inventory(context, telegram_id, status, message):
    name = database.get_employee_name(telegram_id)
    date, time = database.get_current_datetime_strings()
    status_label = "❌ Закончилось" if status == "out" else "⚠️ Заканчивается"

    text = (
        f"{status_label}\n\n"
        f"👤 Сотрудник: {name}\n"
        f"📅 Дата: {date}\n"
        f"🕒 Время: {time}\n"
        f"📝 Сообщение: {message}"
    )

    await _send_to_recipients(context, telegram_id, text)


async def notify_closing_area(
    context,
    telegram_id,
    area,
    comment="",
    photos=None,
    extra_text="",
):
    name = database.get_employee_name(telegram_id)
    date, time = database.get_current_datetime_strings()
    area_label = "Касса" if area == "cash" else "Бар"
    comment_text = comment if comment else "—"
    photos = photos or []

    text = (
        "🌙 Выполнен чек-лист вечер\n\n"
        f"👤 Сотрудник: {name}\n"
        f"📌 Раздел: {area_label}\n"
        f"📅 Дата: {date}\n"
        f"🕒 Время: {time}\n"
    )

    if extra_text:
        text += f"{extra_text}\n"

    text += f"💬 Комментарий: {comment_text}"

    await _send_to_recipients(context, telegram_id, text, photos)


async def notify_handover(context, telegram_id, handover_id):
    handover = database.get_handover_by_id(handover_id)

    if not handover:
        return

    _, _, date, time, comment, status = handover
    name = database.get_employee_name(telegram_id)
    comment_text = comment if comment else "—"

    text = (
        "🔄 Выполнен чек-лист пересменка\n\n"
        f"👤 Сотрудник: {name}\n"
        f"📅 Дата: {date}\n"
        f"🕒 Время: {time}\n"
        f"✅ Статус: {status}\n"
        f"💬 Комментарий: {comment_text}"
    )

    await _send_to_recipients(context, telegram_id, text)
