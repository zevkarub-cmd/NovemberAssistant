from telegram.ext import Application, MessageHandler, filters

from closing_cash_form import closing_cash_form
from config import BOT_TOKEN
from closing_comment import closing_comment
from handlers.broadcast import broadcast_message, start_broadcast
from handlers.checklist_editor import (
    checklist_editor_handler,
    checklist_editor_text,
    start_checklist_editor,
)
from handlers.debug import debug_handler
from handlers.employees import (
    employee_birthday_text,
    employees_handler,
    start_employees,
)
from handlers.handover import handover_comment
from handlers.history import (
    history_handler,
    start_history,
)
from handlers.inline_checklist import (
    bar_inventory_photo_done_handler,
    closing_area_handler,
    closing_handler,
    handover_handler,
    opening_handler,
    start_closing,
    start_handover,
    start_opening,
)
from handlers.inventory import (
    inventory_callback_handler,
    inventory_message,
    start_inventory,
)
from handlers.photos import receive_photo
from handlers.private_only import private_only_handler
from handlers.registration import registration_handler
from opening_form import opening_form


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Incoming updates from groups/supergroups/forums/topics are ignored.
    # Outgoing notifications (including accounting) keep working as usual.
    app.add_handler(private_only_handler, group=-1)

    app.add_handler(registration_handler)
    app.add_handler(debug_handler)

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^☀️ Открытие смены$"),
            start_opening,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🌙 Закрытие смены$"),
            start_closing,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🔄 Пересменка$"),
            start_handover,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📦 Остатки$"),
            start_inventory,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📊 История$"),
            start_history,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^👥 Сотрудники$"),
            start_employees,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📝 Управление чек-листами$"),
            start_checklist_editor,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📢 Сообщение всем$"),
            start_broadcast,
        )
    )

    app.add_handler(closing_area_handler)
    app.add_handler(bar_inventory_photo_done_handler)
    app.add_handler(opening_handler)
    app.add_handler(closing_handler)
    app.add_handler(handover_handler)
    app.add_handler(inventory_callback_handler)
    app.add_handler(employees_handler)
    app.add_handler(checklist_editor_handler)
    app.add_handler(history_handler)

    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))

    # Broad text handlers live in separate groups so state-specific handlers
    # can each inspect the same incoming message.
    app.add_handler(MessageHandler(filters.TEXT, checklist_editor_text), group=1)
    app.add_handler(MessageHandler(filters.TEXT, employee_birthday_text), group=2)
    app.add_handler(MessageHandler(filters.TEXT, broadcast_message), group=3)
    app.add_handler(MessageHandler(filters.TEXT, opening_form), group=4)
    app.add_handler(MessageHandler(filters.TEXT, handover_comment), group=5)
    app.add_handler(MessageHandler(filters.TEXT, inventory_message), group=6)
    app.add_handler(MessageHandler(filters.TEXT, closing_cash_form), group=7)
    app.add_handler(MessageHandler(filters.TEXT, closing_comment), group=8)

    print("November Assistant запущен")

    app.run_polling()


if __name__ == "__main__":
    main()
