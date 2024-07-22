from pyrogram import Client, enums
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FSUB_ID = -1002051607559

async def check_subscription(app: Client, user_id: int) -> bool:
    try:
        chat_member = await app.get_chat_member(FSUB_ID, user_id)
        return chat_member.status in {
            enums.ChatMemberStatus.MEMBER,
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER
        }
    except (enums.FloodWait, enums.UserNotParticipant) as e:
        logger.error(f"Error checking subscription: {e}")
        return False
    except Exception as e:
        logger.exception("Unexpected error during subscription check")
        return False
