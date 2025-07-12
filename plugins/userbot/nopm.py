# plugins/userbot/nopm.py — نسخه بازنویسی شده با Telethon

from telethon import events
from user import USER
from config import Config

msg = Config.msg
REPLY_MESSAGE = Config.REPLY_MESSAGE

@USER.on(events.NewMessage(incoming=True, chats=None))
async def nopm(event):
    if event.is_private and not event.sender.bot and event.sender_id not in [777000, 454000]:
        try:
            # حذف پیام قبلی
            old = msg.get(event.sender_id)
            if old:
                await USER.delete_messages(event.sender_id, [old["msg_id"], old["s_id"]])
            
            # ارسال پیام جدید
            m = await event.respond(f"{REPLY_MESSAGE}\n\n<b>© Powered By :\n@AsmSafone | @AsmSupport 👑</b>")
            
            msg[event.sender_id] = {"msg_id": m.id, "s_id": event.id}
        
        except Exception as e:
            print(f"خطا در nopm: {e}")
