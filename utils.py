from datetime import datetime
from zoneinfo import ZoneInfo

IRKUTSK_TZ = ZoneInfo("Asia/Irkutsk")


def now_irkutsk():
    return datetime.now(IRKUTSK_TZ)


def get_current_datetime_strings():
    now = now_irkutsk()
    return now.strftime("%d.%m.%Y"), now.strftime("%H:%M")


def parse_amount(text):
    cleaned = text.strip().replace(" ", "").replace(",", ".")
    value = float(cleaned)

    if value < 0:
        raise ValueError("amount must be non-negative")

    return value


def format_amount(value):
    value = value or 0

    if value == int(value):
        return str(int(value))

    return f"{value:.2f}".rstrip("0").rstrip(".")
