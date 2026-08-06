from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

import checklist_service
import database
from keyboards import get_main_keyboard
from roles import can_manage_checklists, can_use_bot


def _check_access(telegram_id):
    role = database.get_employee_role(telegram_id)
    return can_use_bot(role) and can_manage_checklists(role)


def checklist_types_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    checklist_service.CHECKLIST_LABELS[checklist_type],
                    callback_data=f"cl_type_{checklist_type}",
                )
            ]
            for checklist_type in checklist_service.ALL_CHECKLIST_TYPES
        ]
    )


def checklist_items_keyboard(checklist_type):
    buttons = []
    items = checklist_service.get_items(checklist_type)

    for index, item in enumerate(items, start=1):
        item_id, _, text, _, assignee, _ = item
        label = f"{index}. {text}"

        if checklist_type == checklist_service.CHECKLIST_CLOSING:
            label = f"{label} [{checklist_service.ASSIGNEE_LABELS.get(assignee, 'Все')}]"

        buttons.append(
            [
                InlineKeyboardButton(
                    label[:64],
                    callback_data=f"cl_item_{item_id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "➕ Добавить пункт",
                callback_data=f"cl_add_{checklist_type}",
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                "⬅️ К типам чек-листов",
                callback_data="cl_types",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def item_actions_keyboard(item_id):
    item = checklist_service.get_item(item_id)

    if not item:
        return InlineKeyboardMarkup([])

    _, checklist_type, _, _, assignee, _ = item
    buttons = [
        [
            InlineKeyboardButton("✏️ Изменить текст", callback_data=f"cl_edit_{item_id}"),
        ],
        [
            InlineKeyboardButton("⬆️ Выше", callback_data=f"cl_up_{item_id}"),
            InlineKeyboardButton("⬇️ Ниже", callback_data=f"cl_down_{item_id}"),
        ],
    ]

    if checklist_type == checklist_service.CHECKLIST_CLOSING:
        next_assignee = {
            checklist_service.ASSIGNEE_ALL: checklist_service.ASSIGNEE_FIRST,
            checklist_service.ASSIGNEE_FIRST: checklist_service.ASSIGNEE_SECOND,
            checklist_service.ASSIGNEE_SECOND: checklist_service.ASSIGNEE_ALL,
        }.get(assignee, checklist_service.ASSIGNEE_ALL)

        buttons.append(
            [
                InlineKeyboardButton(
                    "👥 Сменить назначение",
                    callback_data=f"cl_assignee_{item_id}_{next_assignee}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton("🗑 Удалить", callback_data=f"cl_delete_{item_id}"),
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                "⬅️ К чек-листу",
                callback_data=f"cl_type_{checklist_type}",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


async def start_checklist_editor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = database.get_employee_role(update.effective_user.id)

    if not can_use_bot(role):
        return

    if not can_manage_checklists(role):
        await update.message.reply_text("У вас нет доступа к управлению чек-листами.")
        return

    context.user_data.clear()

    await update.message.reply_text(
        "📝 Управление чек-листами\n\nВыберите чек-лист:",
        reply_markup=checklist_types_keyboard(),
    )


async def checklist_editor_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not _check_access(update.effective_user.id):
        await query.message.reply_text("У вас нет доступа к управлению чек-листами.")
        return

    data = query.data

    if data == "cl_types":
        await query.edit_message_text(
            "📝 Управление чек-листами\n\nВыберите чек-лист:",
            reply_markup=checklist_types_keyboard(),
        )
        return

    if data.startswith("cl_type_"):
        checklist_type = data.replace("cl_type_", "", 1)
        label = checklist_service.CHECKLIST_LABELS.get(checklist_type, checklist_type)

        await query.edit_message_text(
            f"📝 {label}\n\nВыберите пункт или добавьте новый:",
            reply_markup=checklist_items_keyboard(checklist_type),
        )
        return

    if data.startswith("cl_item_"):
        item_id = int(data.split("_")[2])
        item = checklist_service.get_item(item_id)

        if not item:
            await query.message.reply_text("Пункт не найден.")
            return

        _, checklist_type, text, position, assignee, _ = item
        assignee_text = checklist_service.ASSIGNEE_LABELS.get(assignee, "Все")

        await query.edit_message_text(
            f"Пункт #{position}\n\n"
            f"{text}\n\n"
            f"Назначение: {assignee_text}",
            reply_markup=item_actions_keyboard(item_id),
        )
        return

    if data.startswith("cl_add_"):
        checklist_type = data.replace("cl_add_", "", 1)
        context.user_data["checklist_editor_stage"] = "add"
        context.user_data["checklist_editor_type"] = checklist_type

        await query.edit_message_text("Введите текст нового пункта:")
        return

    if data.startswith("cl_edit_"):
        item_id = int(data.split("_")[2])
        context.user_data["checklist_editor_stage"] = "edit"
        context.user_data["checklist_editor_item_id"] = item_id

        await query.edit_message_text("Введите новый текст пункта:")
        return

    if data.startswith("cl_delete_"):
        item_id = int(data.split("_")[2])
        item = checklist_service.get_item(item_id)

        if not item:
            await query.message.reply_text("Пункт не найден.")
            return

        checklist_type = item[1]
        checklist_service.delete_item(item_id)

        await query.edit_message_text(
            "Пункт удалён.",
            reply_markup=checklist_items_keyboard(checklist_type),
        )
        return

    if data.startswith("cl_up_") or data.startswith("cl_down_"):
        parts = data.split("_")
        direction = parts[1]
        item_id = int(parts[2])
        item = checklist_service.get_item(item_id)

        if not item:
            await query.message.reply_text("Пункт не найден.")
            return

        checklist_type = item[1]
        checklist_service.move_item(item_id, direction)

        await query.edit_message_text(
            "Порядок обновлён.",
            reply_markup=checklist_items_keyboard(checklist_type),
        )
        return

    if data.startswith("cl_assignee_"):
        parts = data.split("_", 3)
        item_id = int(parts[2])
        assignee = parts[3]
        item = checklist_service.get_item(item_id)

        if not item:
            await query.message.reply_text("Пункт не найден.")
            return

        checklist_service.set_assignee(item_id, assignee)
        updated_item = checklist_service.get_item(item_id)
        checklist_type = updated_item[1]

        await query.edit_message_text(
            "Назначение обновлено.",
            reply_markup=checklist_items_keyboard(checklist_type),
        )


async def checklist_editor_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stage = context.user_data.get("checklist_editor_stage")

    if stage not in {"add", "edit"}:
        return

    if not _check_access(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к управлению чек-листами.")
        return

    text = update.message.text.strip()

    if not text:
        await update.message.reply_text("Текст пункта не может быть пустым.")
        return

    if stage == "add":
        checklist_type = context.user_data.get("checklist_editor_type")
        checklist_service.add_item(checklist_type, text)
    else:
        item_id = context.user_data.get("checklist_editor_item_id")
        item = checklist_service.get_item(item_id)

        if not item:
            await update.message.reply_text("Пункт не найден.")
            context.user_data.pop("checklist_editor_stage", None)
            return

        checklist_type = item[1]
        checklist_service.update_item_text(item_id, text)

    role = database.get_employee_role(update.effective_user.id)

    context.user_data.pop("checklist_editor_stage", None)
    context.user_data.pop("checklist_editor_type", None)
    context.user_data.pop("checklist_editor_item_id", None)

    await update.message.reply_text(
        "✅ Чек-лист обновлён.",
        reply_markup=get_main_keyboard(role),
    )
    await update.message.reply_text(
        "Открываю обновлённый чек-лист:",
        reply_markup=checklist_items_keyboard(checklist_type),
    )


checklist_editor_handler = CallbackQueryHandler(
    checklist_editor_callback,
    pattern=r"^cl_",
)
