from telegram import Chat, Update
from telegram.ext import ApplicationHandlerStop, ContextTypes, TypeHandler

from config import OWNER_TELEGRAM_ID


async def ignore_non_private_updates(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    chat = update.effective_chat

    if chat is None:
        return

    # Private chats: normal employee bot flow.
    if chat.type == Chat.PRIVATE:
        return

    # Groups / supergroups / forums / topics:
    # only the owner can interact with the bot there.
    user = update.effective_user

    if OWNER_TELEGRAM_ID and user and user.id == OWNER_TELEGRAM_ID:
        return

    raise ApplicationHandlerStop


private_only_handler = TypeHandler(Update, ignore_non_private_updates)
