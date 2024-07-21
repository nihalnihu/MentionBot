
from pyrogram import Client, filters, enums
import asyncio
import logging
import stats

api_id = 25731065
api_hash = 'be534fb5a5afd8c3308c9ca92afde672'
bot_token = '6865008064:AAHfTdmqXhrd-P-2Og2Mu-I5z9_Rh9WQMCY'
OWNER_ID = 7220858548

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot
app = Client("mention_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def is_user_admin(chat_id, user_id):
    try:
        chat_member = await app.get_chat_member(chat_id, user_id)
        status = chat_member.status
        logger.info(f"Fetched chat member status: {status} for user_id: {user_id}")

        if status in {enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER}:
            return True
        return False
    except Exception as e:
        logger.error(f"Error fetching chat member status for user_id {user_id}: {e}")
        return False

@app.on_message(filters.command("mention") & filters.group)
async def mention(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    logger.info(f"Chat ID: {chat_id}, User ID: {user_id}")

    is_admin = await is_user_admin(chat_id, user_id)
    logger.info(f"User admin status: {is_admin}")

    if not is_admin:
        await message.delete()
        return

    command_parts = message.text.split(maxsplit=1)
    mentions = []

    async for member in app.get_chat_members(chat_id):
        if not member.user.is_bot:
            if member.user.username:
                mentions.append(f"@{member.user.username}")
            else:
                mentions.append(f"[{member.user.first_name}](tg://user?id={member.user.id})")

    if len(command_parts) > 1:
        custom_message = command_parts[1]
        mention_chunks = [", ".join(mentions[i:i + 5]) for i in range(0, len(mentions), 5)]
        for chunk in mention_chunks:
            full_message = f"{custom_message}\n\n{chunk}"
            await message.reply(full_message)
            await asyncio.sleep(2)
    else:
        mention_chunks = [", ".join(mentions[i:i + 5]) for i in range(0, len(mentions), 5)]
        for chunk in mention_chunks:
            full_message = chunk
            await message.reply(full_message)
            await asyncio.sleep(1)



@app.on_message(filters.command("broadcast") & filters.group)
async def broadcast_to_members(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    failed_count = 0
    done_count = 0

    logger.info(f"Chat ID: {chat_id}, User ID: {user_id}")

    is_admin = await is_user_admin(chat_id, user_id)
    logger.info(f"User admin status: {is_admin}")

    if not is_admin:
        await message.delete()
        return

    if message.reply_to_message:
        replied_message = message.reply_to_message
        reply_markup = replied_message.reply_markup
        text = replied_message.text or ""
        caption = replied_message.caption or ""

        media_type = None
        media = None

        if replied_message.photo:
            media_type = "photo"
            media = (replied_message.photo.file_id, caption)
        elif replied_message.video:
            media_type = "video"
            media = (replied_message.video.file_id, caption)
        elif replied_message.sticker:
            media_type = "sticker"
            media = (replied_message.sticker.file_id,)
        else:
            media_type = "text"
            media = (text,)

        reply_message = await message.reply(f"Broadcasting {media_type}...")

        async for member in app.get_chat_members(chat_id):
            if not member.user.is_bot:
                try:
                    if media_type == "photo":
                        if caption and reply_markup:
                            await client.send_photo(member.user.id, media[0], caption=media[1], reply_markup=reply_markup)
                        elif caption:
                            await client.send_photo(member.user.id, media[0], caption=media[1])
                        elif reply_markup:
                            await client.send_photo(member.user.id, media[0], reply_markup=reply_markup)
                        else:
                            await client.send_photo(member.user.id, media[0])
                    elif media_type == "video":
                        if caption and reply_markup:
                            await client.send_video(member.user.id, media[0], caption=media[1], reply_markup=reply_markup)
                        elif caption:
                            await client.send_video(member.user.id, media[0], caption=media[1])
                        elif reply_markup:
                            await client.send_video(member.user.id, media[0], reply_markup=reply_markup)
                        else:
                            await client.send_video(member.user.id, media[0])
                    elif media_type == "sticker":
                        if reply_markup:
                            await client.send_sticker(member.user.id, media[0], reply_markup=reply_markup)
                        else:
                            await client.send_sticker(member.user.id, media[0])
                    elif media_type == "text":
                        if reply_markup:
                            await client.send_message(member.user.id, media[0], reply_markup=reply_markup)
                        else:
                            await client.send_message(member.user.id, media[0])
                    done_count += 1
                    await asyncio.sleep(1)  # To avoid hitting rate limits
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send {media_type} to user {member.user.id}: {e}")

        await reply_message.edit(f"Total Members: {done_count + failed_count}\nSuccessfully Sent: {done_count}\nFailed: {failed_count}")

    else:
        command_parts = message.text.split(maxsplit=1)

        if len(command_parts) > 1:
            custom_message = command_parts[1]
            reply_message = await message.reply("Broadcasting text message...")

            async for member in app.get_chat_members(chat_id):
                if not member.user.is_bot:
                    try:
                        await client.send_message(member.user.id, custom_message)
                        done_count += 1
                        await asyncio.sleep(1)
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Failed to send message to user {member.user.id}: {e}")

            await reply_message.edit(f"Total Members: {done_count + failed_count}\nSuccessfully Sent: {done_count}\nFailed: {failed_count}")

        else:
            await message.reply("Usage: /broadcast <message> or reply to a photo, video, or sticker with /broadcast")






@app.on_message(filters.command("bc") & filters.private & filters.user(OWNER_ID))
async def broadcast(client, message):
    command_parts = message.text.split(maxsplit=1)
    failed_count = 0
    done_count = 0

    if message.reply_to_message:
        replied_message = message.reply_to_message
        reply_markup = replied_message.reply_markup
        text = replied_message.text or ""
        caption = replied_message.caption or ""

        if replied_message.photo:
            media_type = "photo"
            media = (replied_message.photo.file_id, caption)
        elif replied_message.video:
            media_type = "video"
            media = (replied_message.video.file_id, caption)
        elif replied_message.sticker:
            media_type = "sticker"
            media = (replied_message.sticker.file_id,)
        else:
            media_type = "text"
            media = (text,)

        if reply_markup:
            reply_message = await message.reply(f"Broadcasting {media_type} with buttons...")

            user_ids = stats.get_all_user_ids()
            for user_id in user_ids:
                try:
                    if media_type == "photo":
                        await client.send_photo(
                            user_id,
                            media[0],
                            caption=media[1],
                            reply_markup=reply_markup
                        )
                    elif media_type == "video":
                        await client.send_video(
                            user_id,
                            media[0],
                            caption=media[1],
                            reply_markup=reply_markup
                        )
                    elif media_type == "sticker":
                        await client.send_sticker(
                            user_id,
                            media[0],
                            reply_markup=reply_markup
                        )
                    elif media_type == "text":
                        await client.send_message(
                            user_id,
                            media[0],
                            reply_markup=reply_markup
                        )
                    done_count += 1
                    await asyncio.sleep(1)  # To avoid hitting rate limits
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send {media_type} with buttons to user {user_id}: {e}")

            await reply_message.edit(f"Total Users: {done_count + failed_count}\nSuccessfully Sent: {done_count}\nFailed: {failed_count}")
        else:
            await message.reply("The replied message must contain buttons.")

    else:
        if len(command_parts) > 1:
            custom_message = command_parts[1]
            reply_message = await message.reply("Broadcasting text message...")

            user_ids = stats.get_all_user_ids()
            for user_id in user_ids:
                try:
                    await client.send_message(user_id, custom_message)
                    done_count += 1
                    await asyncio.sleep(1)
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send message to user {user_id}: {e}")

            await reply_message.edit(f"Total Users: {done_count + failed_count}\nSuccessfully Sent: {done_count}\nFailed: {failed_count}")

        else:
            await message.reply("Usage: /bc <message> or reply to a photo, video, or sticker with /bc")


app.run()
