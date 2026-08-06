from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")

_owner_id = os.getenv("OWNER_TELEGRAM_ID", "").strip()
OWNER_TELEGRAM_ID = int(_owner_id) if _owner_id.isdigit() else None

_accounting_chat_id = os.getenv("ACCOUNTING_CHAT_ID", "").strip()
ACCOUNTING_CHAT_ID = (
    int(_accounting_chat_id)
    if _accounting_chat_id.lstrip("-").isdigit()
    else None
)

_accounting_message_thread_id = os.getenv(
    "ACCOUNTING_MESSAGE_THREAD_ID",
    "",
).strip()
ACCOUNTING_MESSAGE_THREAD_ID = (
    int(_accounting_message_thread_id)
    if _accounting_message_thread_id.isdigit()
    else None
)
