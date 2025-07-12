# user.py >> Telethon

from telethon import TelegramClient
from telethon.sessions import StringSession
from config import Config

REPLY_MESSAGE = Config.REPLY_MESSAGE

if REPLY_MESSAGE is not None:
    USER = TelegramClient(
        session=StringSession(Config.SESSION),
        api_id=Config.API_ID,
        api_hash=Config.API_HASH
    )
else:
    USER = None
