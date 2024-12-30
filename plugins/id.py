from pyrogram import Client, filters, enums
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.command('id'))
async def show_id(client, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text(f"<b>» ᴜꜱᴇʀ ɪᴅ - <code>{message.from_user.id}</code></b>")

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply_text(f"<b>» ɢʀᴏᴜᴘ ɪᴅ - <code>{message.chat.id}</code></b>")

    elif chat_type == enums.ChatType.CHANNEL:
        await message.reply_text(f"<b>» ᴄʜᴀɴɴᴇʟ ɪᴅ - <code>{message.chat.id}</code></b>")


# THANKS TO NISHANT
# CREDIT @IM_NISHANTT
# PLZ.. DON'T REMOVE THIS CREDIT
# CONTACT FOR DOUBTS ON TG - @IM_NISHANT
#--------------------------------------------------------------------------👻👻👻👻👻👻--------------------------------------------------------------------------