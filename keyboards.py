from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from roles import (
    can_broadcast,
    can_manage_checklists,
    can_use_bot,
    can_view_employees,
    can_view_history,
)


def get_main_keyboard(role):
    if not can_use_bot(role):
        return ReplyKeyboardRemove()

    keyboard = [
        ["☀️ Открытие смены"],
        ["🌙 Закрытие смены"],
        ["🔄 Пересменка"],
        ["📦 Остатки"],
    ]

    if can_view_history(role):
        keyboard.append(["📊 История"])

    owner_row = []

    if can_view_employees(role):
        owner_row.append("👥 Сотрудники")

    if can_manage_checklists(role):
        owner_row.append("📝 Управление чек-листами")

    if owner_row:
        keyboard.append(owner_row)

    if can_broadcast(role):
        keyboard.append(["📢 Сообщение всем"])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие...",
    )


main_keyboard = get_main_keyboard("barista")