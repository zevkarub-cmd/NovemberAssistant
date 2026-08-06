import sqlite3

from config import OWNER_TELEGRAM_ID
from roles import (
    BROADCAST_EXCLUDED_ROLES,
    ROLE_BARISTA,
    ROLE_MANAGER,
    ROLE_OWNER,
    ROLE_VERIFICATION,
)
from utils import get_current_datetime_strings

DB_NAME = "database.db"

connection = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = connection.cursor()


def _execute_schema():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        telegram_id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS openings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        date TEXT,
        time TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opening_photos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opening_id INTEGER,
        showcase_photo TEXT,
        coffee_photo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS closings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        date TEXT,
        time TEXT,
        comment TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS closing_photos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        closing_id INTEGER,
        showcase_photo TEXT,
        holder_photo TEXT,
        coffee_photo TEXT,
        bar_photo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        date TEXT,
        time TEXT,
        status TEXT,
        message TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklist_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checklist_type TEXT,
        text TEXT,
        position INTEGER,
        assignee TEXT DEFAULT 'all',
        is_active INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS handovers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        date TEXT,
        time TEXT,
        comment TEXT,
        status TEXT DEFAULT 'completed'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS closing_sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        starter_id INTEGER,
        partner_id INTEGER,
        status TEXT,
        created_date TEXT,
        created_time TEXT,
        starter_done INTEGER DEFAULT 0,
        partner_done INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS closing_inventory_photos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        date TEXT,
        time TEXT,
        file_id TEXT
    )
    """)

    connection.commit()


def _ensure_column(table, column, column_type):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]

    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
        connection.commit()


def _migrate_checklist_item_prefix_cleanup():
    """Remove category prefixes from checklist texts (idempotent)."""
    prefixes = (
        "Передача информации: ",
        "Общее: ",
        "Кофе и напитки: ",
        "Проверка зон: ",
        "Касса: ",
        "Бар: ",
    )

    cursor.execute("SELECT id, text FROM checklist_items")
    rows = cursor.fetchall()
    updated = False

    for item_id, text in rows:
        if not text:
            continue

        new_text = text
        changed = True

        while changed:
            changed = False
            for prefix in prefixes:
                if new_text.startswith(prefix):
                    new_text = new_text[len(prefix):]
                    changed = True
                    break

                # Also strip after a leading emoji + space, e.g. "💵 Касса: ..."
                parts = new_text.split(" ", 1)
                if len(parts) == 2 and parts[1].startswith(prefix):
                    new_text = f"{parts[0]} {parts[1][len(prefix):]}"
                    changed = True
                    break

        new_text = " ".join(new_text.split())

        if new_text != text:
            cursor.execute(
                "UPDATE checklist_items SET text=? WHERE id=?",
                (new_text, item_id),
            )
            updated = True

    if updated:
        connection.commit()


def _execute_migrations():
    _ensure_column("employees", "role", f"TEXT DEFAULT '{ROLE_BARISTA}'")
    _ensure_column("employees", "registered_at", "TEXT")
    _ensure_column("employees", "birthday", "TEXT")
    _ensure_column("openings", "comment", "TEXT DEFAULT ''")
    _ensure_column("openings", "opening_cash", "REAL DEFAULT 0")
    _ensure_column("closings", "telegram_id_2", "INTEGER")
    _ensure_column("closings", "mode", "TEXT DEFAULT 'solo'")
    _ensure_column("closings", "status", "TEXT DEFAULT 'completed'")
    _ensure_column("closings", "total_revenue", "REAL DEFAULT 0")
    _ensure_column("closings", "card_revenue", "REAL DEFAULT 0")
    _ensure_column("closings", "cash_revenue", "REAL DEFAULT 0")
    _ensure_column("closings", "change_amount", "REAL DEFAULT 0")
    _ensure_column("closings", "largest_check", "REAL DEFAULT 0")
    _ensure_column("closings", "cashbox_amount", "REAL DEFAULT 0")
    _ensure_column("closings", "refunds_amount", "REAL DEFAULT 0")
    _migrate_checklist_item_prefix_cleanup()


_execute_schema()
_execute_migrations()


def employee_exists(telegram_id):
    cursor.execute(
        "SELECT 1 FROM employees WHERE telegram_id=?",
        (telegram_id,),
    )
    return cursor.fetchone() is not None


def _initial_role(telegram_id):
    if OWNER_TELEGRAM_ID and telegram_id == OWNER_TELEGRAM_ID:
        return ROLE_OWNER

    return ROLE_VERIFICATION


def add_employee(telegram_id, name):
    date, time = get_current_datetime_strings()

    if employee_exists(telegram_id):
        cursor.execute(
            "UPDATE employees SET name=? WHERE telegram_id=?",
            (name, telegram_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO employees(telegram_id, name, role, registered_at)
            VALUES (?, ?, ?, ?)
            """,
            (telegram_id, name, _initial_role(telegram_id), f"{date} {time}"),
        )

    connection.commit()


def get_employee_name(telegram_id):
    cursor.execute(
        "SELECT name FROM employees WHERE telegram_id=?",
        (telegram_id,),
    )
    row = cursor.fetchone()
    return row[0] if row else "Неизвестно"


def get_employee_role(telegram_id):
    cursor.execute(
        "SELECT role FROM employees WHERE telegram_id=?",
        (telegram_id,),
    )
    row = cursor.fetchone()
    return row[0] if row and row[0] else ROLE_VERIFICATION


def update_employee_role(telegram_id, role):
    cursor.execute(
        "UPDATE employees SET role=? WHERE telegram_id=?",
        (role, telegram_id),
    )
    connection.commit()


def update_employee_birthday(telegram_id, birthday):
    cursor.execute(
        "UPDATE employees SET birthday=? WHERE telegram_id=?",
        (birthday, telegram_id),
    )
    connection.commit()


def get_all_employees():
    cursor.execute("""
        SELECT telegram_id, name, role, registered_at, birthday
        FROM employees
        ORDER BY name COLLATE NOCASE
    """)
    return cursor.fetchall()


def get_employee_info(telegram_id):
    cursor.execute(
        """
        SELECT telegram_id, name, role, registered_at, birthday
        FROM employees
        WHERE telegram_id=?
        """,
        (telegram_id,),
    )
    return cursor.fetchone()


def get_employee_stats(telegram_id):
    cursor.execute("SELECT COUNT(*) FROM openings WHERE telegram_id=?", (telegram_id,))
    openings_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM closings WHERE telegram_id=? OR telegram_id_2=?",
        (telegram_id, telegram_id),
    )
    closings_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COALESCE(SUM(total_revenue), 0), COALESCE(MAX(largest_check), 0)
        FROM closings
        WHERE telegram_id=? OR telegram_id_2=?
        """,
        (telegram_id, telegram_id),
    )
    total_revenue, largest_check = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM handovers WHERE telegram_id=?", (telegram_id,))
    handovers_count = cursor.fetchone()[0]

    return {
        "openings_count": openings_count,
        "closings_count": closings_count,
        "handovers_count": handovers_count,
        "total_revenue": total_revenue,
        "largest_check": largest_check,
    }


def get_notification_recipients():
    cursor.execute(
        "SELECT telegram_id FROM employees WHERE role IN (?, ?)",
        (ROLE_MANAGER, ROLE_OWNER),
    )
    return [row[0] for row in cursor.fetchall()]


def get_broadcast_recipients():
    placeholders = ", ".join("?" for _ in BROADCAST_EXCLUDED_ROLES)
    cursor.execute(
        f"""
        SELECT telegram_id
        FROM employees
        WHERE role NOT IN ({placeholders})
        """,
        BROADCAST_EXCLUDED_ROLES,
    )
    return [row[0] for row in cursor.fetchall()]


def save_opening_now(telegram_id, comment="", opening_cash=0):
    date, time = get_current_datetime_strings()
    cursor.execute(
        """
        INSERT INTO openings(telegram_id, date, time, comment, opening_cash)
        VALUES (?, ?, ?, ?, ?)
        """,
        (telegram_id, date, time, comment, opening_cash),
    )
    connection.commit()
    return cursor.lastrowid


def save_opening(telegram_id, date, time):
    cursor.execute(
        "INSERT INTO openings(telegram_id, date, time) VALUES (?, ?, ?)",
        (telegram_id, date, time),
    )
    connection.commit()
    return cursor.lastrowid


def save_opening_photos(opening_id, showcase_photo, coffee_photo):
    cursor.execute(
        """
        INSERT INTO opening_photos(opening_id, showcase_photo, coffee_photo)
        VALUES (?, ?, ?)
        """,
        (opening_id, showcase_photo, coffee_photo),
    )
    connection.commit()


def get_opening_by_id(opening_id):
    cursor.execute(
        """
        SELECT id, telegram_id, date, time, comment, opening_cash
        FROM openings
        WHERE id=?
        """,
        (opening_id,),
    )
    return cursor.fetchone()


def get_opening_photos(opening_id):
    cursor.execute(
        """
        SELECT showcase_photo, coffee_photo
        FROM opening_photos
        WHERE opening_id=?
        """,
        (opening_id,),
    )
    return cursor.fetchone()


def save_closing_now(
    telegram_id,
    comment="",
    total_revenue=0,
    card_revenue=0,
    cash_revenue=0,
    change_amount=0,
    largest_check=0,
    telegram_id_2=None,
    mode="solo",
    cashbox_amount=0,
    refunds_amount=0,
):
    date, time = get_current_datetime_strings()
    cursor.execute(
        """
        INSERT INTO closings(
            telegram_id,
            telegram_id_2,
            date,
            time,
            comment,
            mode,
            status,
            total_revenue,
            card_revenue,
            cash_revenue,
            change_amount,
            largest_check,
            cashbox_amount,
            refunds_amount
        )
        VALUES (?, ?, ?, ?, ?, ?, 'completed', ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            telegram_id,
            telegram_id_2,
            date,
            time,
            comment,
            mode,
            total_revenue,
            card_revenue,
            cash_revenue,
            change_amount,
            largest_check,
            cashbox_amount,
            refunds_amount,
        ),
    )
    connection.commit()
    return cursor.lastrowid


def save_closing_photos(
    closing_id,
    showcase_photo,
    holder_photo,
    coffee_photo,
    bar_photo,
):
    cursor.execute(
        """
        INSERT INTO closing_photos(
            closing_id,
            showcase_photo,
            holder_photo,
            coffee_photo,
            bar_photo
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (closing_id, showcase_photo, holder_photo, coffee_photo, bar_photo),
    )
    connection.commit()


def get_closing_by_id(closing_id):
    cursor.execute(
        """
        SELECT
            id,
            telegram_id,
            telegram_id_2,
            date,
            time,
            comment,
            mode,
            total_revenue,
            card_revenue,
            cash_revenue,
            change_amount,
            largest_check
        FROM closings
        WHERE id=?
        """,
        (closing_id,),
    )
    return cursor.fetchone()


def get_closing_photos(closing_id):
    cursor.execute(
        """
        SELECT showcase_photo, holder_photo, coffee_photo, bar_photo
        FROM closing_photos
        WHERE closing_id=?
        """,
        (closing_id,),
    )
    return cursor.fetchone()


def create_closing_session(starter_id):
    date, time = get_current_datetime_strings()
    cursor.execute(
        """
        INSERT INTO closing_sessions(starter_id, status, created_date, created_time)
        VALUES (?, 'waiting_partner', ?, ?)
        """,
        (starter_id, date, time),
    )
    connection.commit()
    return cursor.lastrowid


def get_waiting_closing_session():
    cursor.execute(
        """
        SELECT id, starter_id, partner_id, status, starter_done, partner_done
        FROM closing_sessions
        WHERE status='waiting_partner'
        ORDER BY id DESC
        LIMIT 1
        """
    )
    return cursor.fetchone()


def get_closing_session(session_id):
    cursor.execute(
        """
        SELECT id, starter_id, partner_id, status, starter_done, partner_done
        FROM closing_sessions
        WHERE id=?
        """,
        (session_id,),
    )
    return cursor.fetchone()


def join_closing_session(session_id, partner_id):
    cursor.execute(
        """
        UPDATE closing_sessions
        SET partner_id=?, status='in_progress'
        WHERE id=? AND status='waiting_partner'
        """,
        (partner_id, session_id),
    )
    connection.commit()


def set_closing_session_done(session_id, employee_number):
    column = "starter_done" if employee_number == 1 else "partner_done"
    cursor.execute(
        f"UPDATE closing_sessions SET {column}=1 WHERE id=?",
        (session_id,),
    )
    connection.commit()


def complete_closing_session(session_id):
    cursor.execute(
        "UPDATE closing_sessions SET status='completed' WHERE id=?",
        (session_id,),
    )
    connection.commit()


def save_handover(telegram_id, comment="", status="completed"):
    date, time = get_current_datetime_strings()
    cursor.execute(
        """
        INSERT INTO handovers(telegram_id, date, time, comment, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (telegram_id, date, time, comment, status),
    )
    connection.commit()
    return cursor.lastrowid


def get_handover_by_id(handover_id):
    cursor.execute(
        """
        SELECT id, telegram_id, date, time, comment, status
        FROM handovers
        WHERE id=?
        """,
        (handover_id,),
    )
    return cursor.fetchone()


def save_inventory_message(telegram_id, status, message):
    date, time = get_current_datetime_strings()
    cursor.execute(
        """
        INSERT INTO inventory_messages(telegram_id, date, time, status, message)
        VALUES (?, ?, ?, ?, ?)
        """,
        (telegram_id, date, time, status, message),
    )
    connection.commit()
    return cursor.lastrowid


def save_closing_inventory_photo(telegram_id, file_id):
    date, time = get_current_datetime_strings()
    cursor.execute(
        """
        INSERT INTO closing_inventory_photos(telegram_id, date, time, file_id)
        VALUES (?, ?, ?, ?)
        """,
        (telegram_id, date, time, file_id),
    )
    connection.commit()
    return cursor.lastrowid


def get_openings():
    cursor.execute("SELECT telegram_id, date, time FROM openings ORDER BY id DESC")
    return cursor.fetchall()


def get_openings_full():
    cursor.execute("""
        SELECT
            openings.id,
            openings.telegram_id,
            openings.date,
            openings.time,
            employees.name,
            openings.opening_cash,
            openings.comment
        FROM openings
        LEFT JOIN employees ON openings.telegram_id = employees.telegram_id
        ORDER BY openings.id DESC
    """)
    return cursor.fetchall()


def get_closings_full():
    cursor.execute("""
        SELECT
            closings.id,
            closings.telegram_id,
            closings.telegram_id_2,
            closings.date,
            closings.time,
            first_employee.name,
            second_employee.name,
            closings.total_revenue,
            closings.card_revenue,
            closings.cash_revenue,
            closings.change_amount,
            closings.largest_check,
            closings.comment,
            closings.mode,
            closings.cashbox_amount,
            closings.refunds_amount
        FROM closings
        LEFT JOIN employees AS first_employee
            ON closings.telegram_id = first_employee.telegram_id
        LEFT JOIN employees AS second_employee
            ON closings.telegram_id_2 = second_employee.telegram_id
        ORDER BY closings.id DESC
    """)
    return cursor.fetchall()


def get_handovers_full():
    cursor.execute("""
        SELECT
            handovers.id,
            handovers.telegram_id,
            handovers.date,
            handovers.time,
            employees.name,
            handovers.comment,
            handovers.status
        FROM handovers
        LEFT JOIN employees ON handovers.telegram_id = employees.telegram_id
        ORDER BY handovers.id DESC
    """)
    return cursor.fetchall()


def get_checklist_items(checklist_type, include_inactive=False):
    where = "checklist_type=?"
    params = [checklist_type]

    if not include_inactive:
        where += " AND is_active=1"

    cursor.execute(
        f"""
        SELECT id, checklist_type, text, position, assignee, is_active
        FROM checklist_items
        WHERE {where}
        ORDER BY position, id
        """,
        params,
    )
    return cursor.fetchall()


def get_checklist_item(item_id):
    cursor.execute(
        """
        SELECT id, checklist_type, text, position, assignee, is_active
        FROM checklist_items
        WHERE id=?
        """,
        (item_id,),
    )
    return cursor.fetchone()


def add_checklist_item(checklist_type, text, assignee="all"):
    cursor.execute(
        """
        SELECT COALESCE(MAX(position), 0) + 1
        FROM checklist_items
        WHERE checklist_type=? AND is_active=1
        """,
        (checklist_type,),
    )
    position = cursor.fetchone()[0]
    cursor.execute(
        """
        INSERT INTO checklist_items(checklist_type, text, position, assignee, is_active)
        VALUES (?, ?, ?, ?, 1)
        """,
        (checklist_type, text, position, assignee),
    )
    connection.commit()
    return cursor.lastrowid


def update_checklist_item_text(item_id, text):
    cursor.execute(
        "UPDATE checklist_items SET text=? WHERE id=?",
        (text, item_id),
    )
    connection.commit()


def update_checklist_item_assignee(item_id, assignee):
    cursor.execute(
        "UPDATE checklist_items SET assignee=? WHERE id=?",
        (assignee, item_id),
    )
    connection.commit()


def delete_checklist_item(item_id):
    cursor.execute(
        "UPDATE checklist_items SET is_active=0 WHERE id=?",
        (item_id,),
    )
    connection.commit()


def swap_checklist_item_position(item_id, direction):
    item = get_checklist_item(item_id)

    if not item:
        return

    _, checklist_type, _, position, _, _ = item
    operator = "<" if direction == "up" else ">"
    sort = "DESC" if direction == "up" else "ASC"

    cursor.execute(
        f"""
        SELECT id, position
        FROM checklist_items
        WHERE checklist_type=? AND is_active=1 AND position {operator} ?
        ORDER BY position {sort}
        LIMIT 1
        """,
        (checklist_type, position),
    )
    neighbor = cursor.fetchone()

    if not neighbor:
        return

    neighbor_id, neighbor_position = neighbor

    cursor.execute(
        "UPDATE checklist_items SET position=? WHERE id=?",
        (neighbor_position, item_id),
    )
    cursor.execute(
        "UPDATE checklist_items SET position=? WHERE id=?",
        (position, neighbor_id),
    )
    connection.commit()