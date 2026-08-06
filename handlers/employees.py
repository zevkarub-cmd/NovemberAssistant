from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

import database
from keyboards import get_main_keyboard
from roles import (
    ALL_ROLES,
    ROLE_LABELS,
    ROLE_OWNER,
    can_manage_employees,
    can_use_bot,
    can_view_employees,
    role_label,
)
from config import OWNER_TELEGRAM_ID
from utils import format_amount


def _birthday_text(birthday):
    return birthday if birthday else "Не указана"


def _employee_card_text(employee_id, name, employee_role, birthday):
    return (
        f"👤 {name}\n\n"
        f"🆔 Telegram ID: {employee_id}\n"
        f"👔 Должность: {role_label(employee_role)}\n"
        f"🎂 Дата рождения: {_birthday_text(birthday)}"
    )


def employees_list_keyboard():
    buttons = []

    for telegram_id, name, role, *_ in database.get_all_employees():
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{name} ({role_label(role)})",
                    callback_data=f"emp_view_{telegram_id}",
                )
            ]
        )

    if not buttons:
        return None

    return InlineKeyboardMarkup(buttons)


def employee_actions_keyboard(telegram_id, viewer_role):
    buttons = [
        [
            InlineKeyboardButton(
                "📊 Статистика",
                callback_data=f"emp_stats_{telegram_id}",
            )
        ],
    ]

    if can_manage_employees(viewer_role):
        buttons.append(
            [
                InlineKeyboardButton(
                    "👔 Изменить должность",
                    callback_data=f"emp_roles_{telegram_id}",
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    "🎂 Изменить дату рождения",
                    callback_data=f"emp_birthday_{telegram_id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "⬅️ К списку",
                callback_data="emp_list",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def employee_roles_keyboard(telegram_id):
    buttons = []

    for role in ALL_ROLES:
        buttons.append(
            [
                InlineKeyboardButton(
                    ROLE_LABELS[role],
                    callback_data=f"emp_setrole_{telegram_id}_{role}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"emp_view_{telegram_id}",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def parse_birthday(text):
    cleaned = text.strip()
    datetime.strptime(cleaned, "%d.%m.%Y")
    return cleaned


async def start_employees(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = database.get_employee_role(update.effective_user.id)

    if not can_use_bot(role):
        return

    if not can_view_employees(role):
        await update.message.reply_text("У вас нет доступа к разделу сотрудников.")
        return

    context.user_data.clear()
    keyboard = employees_list_keyboard()

    if not keyboard:
        await update.message.reply_text("👥 Сотрудники\n\nСписок сотрудников пока пуст.")
        return

    await update.message.reply_text(
        "👥 Сотрудники\n\nВыберите сотрудника:",
        reply_markup=keyboard,
    )


async def employees_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    role = database.get_employee_role(update.effective_user.id)

    if not can_use_bot(role):
        return

    if not can_view_employees(role):
        await query.message.reply_text("У вас нет доступа к разделу сотрудников.")
        return

    data = query.data

    if data == "emp_list":
        context.user_data.pop("employee_birthday_stage", None)
        context.user_data.pop("employee_birthday_id", None)
        keyboard = employees_list_keyboard()

        if not keyboard:
            await query.edit_message_text("👥 Сотрудники\n\nСписок сотрудников пока пуст.")
            return

        await query.edit_message_text(
            "👥 Сотрудники\n\nВыберите сотрудника:",
            reply_markup=keyboard,
        )
        return

    if data.startswith("emp_view_"):
        context.user_data.pop("employee_birthday_stage", None)
        context.user_data.pop("employee_birthday_id", None)
        employee_id = int(data.split("_")[2])
        employee = database.get_employee_info(employee_id)

        if not employee:
            await query.message.reply_text("Сотрудник не найден.")
            return

        _, name, employee_role, _, birthday = employee

        await query.edit_message_text(
            _employee_card_text(employee_id, name, employee_role, birthday),
            reply_markup=employee_actions_keyboard(employee_id, role),
        )
        return

    if data.startswith("emp_stats_"):
        employee_id = int(data.split("_")[2])
        employee = database.get_employee_info(employee_id)

        if not employee:
            await query.message.reply_text("Сотрудник не найден.")
            return

        _, name, employee_role, registered_at, birthday = employee
        stats = database.get_employee_stats(employee_id)
        registered_text = registered_at if registered_at else "—"

        await query.edit_message_text(
            f"📊 Статистика: {name}\n\n"
            f"👔 Должность: {role_label(employee_role)}\n"
            f"🎂 Дата рождения: {_birthday_text(birthday)}\n"
            f"📅 Дата регистрации: {registered_text}\n"
            f"☀️ Открытий: {stats['openings_count']}\n"
            f"🌙 Закрытий: {stats['closings_count']}\n"
            f"🔄 Пересменок: {stats['handovers_count']}\n"
            f"💰 Общая выручка: {format_amount(stats['total_revenue'])} ₽\n"
            f"🏆 Самый большой чек: {format_amount(stats['largest_check'])} ₽",
            reply_markup=employee_actions_keyboard(employee_id, role),
        )
        return

    if data.startswith("emp_birthday_"):
        if not can_manage_employees(role):
            await query.message.reply_text(
                "Изменять дату рождения могут только владелец и управляющий."
            )
            return

        employee_id = int(data.split("_")[2])
        context.user_data["employee_birthday_stage"] = "edit"
        context.user_data["employee_birthday_id"] = employee_id

        await query.edit_message_text(
            "🎂 Введите дату рождения в формате:\n\n"
            "ДД.ММ.ГГГГ\n\n"
            "Пример: 15.03.1998"
        )
        return

    if data.startswith("emp_roles_"):
        if not can_manage_employees(role):
            await query.message.reply_text(
                "Изменять должности могут только владелец и управляющий."
            )
            return

        employee_id = int(data.split("_")[2])

        await query.edit_message_text(
            "👔 Выберите новую должность:",
            reply_markup=employee_roles_keyboard(employee_id),
        )
        return

    if data.startswith("emp_setrole_"):
        if not can_manage_employees(role):
            await query.message.reply_text(
                "Изменять должности могут только владелец и управляющий."
            )
            return

        parts = data.split("_", 3)
        employee_id = int(parts[2])
        new_role = parts[3]

        if new_role not in ALL_ROLES:
            return

        target_role = database.get_employee_role(employee_id)

        if (
            employee_id == OWNER_TELEGRAM_ID
            or target_role == ROLE_OWNER
        ) and role != ROLE_OWNER:
            await query.answer(
                "Менять роль владельца может только владелец.",
                show_alert=True,
            )
            return

        if employee_id == OWNER_TELEGRAM_ID and new_role != ROLE_OWNER:
            await query.answer(
                "Нельзя снять роль с владельца бота.",
                show_alert=True,
            )
            return

        database.update_employee_role(employee_id, new_role)
        employee = database.get_employee_info(employee_id)

        if not employee:
            await query.message.reply_text("Сотрудник не найден.")
            return

        _, name, employee_role, _, birthday = employee

        try:
            await context.bot.send_message(
                chat_id=employee_id,
                text=(
                    "✅ Ваша должность обновлена.\n\n"
                    f"👔 Новая должность: {role_label(employee_role)}"
                ),
                reply_markup=get_main_keyboard(employee_role),
            )
        except Exception:
            pass

        await query.edit_message_text(
            "✅ Должность обновлена.\n\n"
            + _employee_card_text(employee_id, name, employee_role, birthday),
            reply_markup=employee_actions_keyboard(employee_id, role),
        )


async def employee_birthday_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("employee_birthday_stage") != "edit":
        return

    role = database.get_employee_role(update.effective_user.id)

    if not can_use_bot(role) or not can_manage_employees(role):
        context.user_data.pop("employee_birthday_stage", None)
        context.user_data.pop("employee_birthday_id", None)
        return

    employee_id = context.user_data.get("employee_birthday_id")
    text = update.message.text.strip()

    try:
        birthday = parse_birthday(text)
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат даты.\n\n"
            "Введите дату рождения в формате:\n"
            "ДД.ММ.ГГГГ\n\n"
            "Пример: 15.03.1998"
        )
        return

    database.update_employee_birthday(employee_id, birthday)
    employee = database.get_employee_info(employee_id)

    context.user_data.pop("employee_birthday_stage", None)
    context.user_data.pop("employee_birthday_id", None)

    if not employee:
        await update.message.reply_text("Сотрудник не найден.")
        return

    _, name, employee_role, _, birthday_value = employee

    await update.message.reply_text(
        "✅ Дата рождения обновлена.\n\n"
        + _employee_card_text(employee_id, name, employee_role, birthday_value),
        reply_markup=employee_actions_keyboard(employee_id, role),
    )


employees_handler = CallbackQueryHandler(
    employees_callback,
    pattern=r"^emp_",
)
