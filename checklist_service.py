import database
from checklists import CLOSE_SHIFT, CLOSE_SHIFT_ASSIGNEES, HANDOVER_SHIFT, OPEN_SHIFT

CHECKLIST_OPENING = "opening"
CHECKLIST_CLOSING = "closing"
CHECKLIST_HANDOVER = "handover"

CHECKLIST_LABELS = {
    CHECKLIST_OPENING: "Открытие смены",
    CHECKLIST_CLOSING: "Закрытие смены",
    CHECKLIST_HANDOVER: "Пересменка",
}

ALL_CHECKLIST_TYPES = (
    CHECKLIST_OPENING,
    CHECKLIST_CLOSING,
    CHECKLIST_HANDOVER,
)

ASSIGNEE_ALL = "all"
ASSIGNEE_FIRST = "first"
ASSIGNEE_SECOND = "second"

ASSIGNEE_LABELS = {
    ASSIGNEE_ALL: "Все",
    ASSIGNEE_FIRST: "Касса",
    ASSIGNEE_SECOND: "Бар",
}


def seed_default_checklists():
    defaults = {
        CHECKLIST_OPENING: [(item, ASSIGNEE_ALL) for item in OPEN_SHIFT],
        CHECKLIST_CLOSING: list(zip(CLOSE_SHIFT, CLOSE_SHIFT_ASSIGNEES)),
        CHECKLIST_HANDOVER: [(item, ASSIGNEE_ALL) for item in HANDOVER_SHIFT],
    }

    for checklist_type, items in defaults.items():
        existing_items = database.get_checklist_items(checklist_type)

        if existing_items:
            continue

        for item, assignee in items:
            database.add_checklist_item(checklist_type, item, assignee)


def get_items(checklist_type, assignee=None, include_inactive=False):
    items = database.get_checklist_items(checklist_type, include_inactive)

    if assignee is None:
        return items

    allowed = {ASSIGNEE_ALL, assignee}

    return [item for item in items if item[4] in allowed]


def add_item(checklist_type, text, assignee=ASSIGNEE_ALL):
    return database.add_checklist_item(checklist_type, text, assignee)


def update_item_text(item_id, text):
    database.update_checklist_item_text(item_id, text)


def delete_item(item_id):
    database.delete_checklist_item(item_id)


def move_item(item_id, direction):
    database.swap_checklist_item_position(item_id, direction)


def set_assignee(item_id, assignee):
    database.update_checklist_item_assignee(item_id, assignee)


def get_item(item_id):
    return database.get_checklist_item(item_id)


seed_default_checklists()
