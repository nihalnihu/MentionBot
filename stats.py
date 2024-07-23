import os
from pyrogram import Client, enums

FSUB_ID = os.getenv('FSUB_ID', 'TG_BotCreator')

async def check_subscription(app: Client, user_id: int):
    try:
        chat_member = await app.get_chat_member(FSUB_ID, user_id)
        return chat_member.status in {enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER}
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False
