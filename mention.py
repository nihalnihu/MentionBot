from pyrogram import Client, filters, enums
import asyncio
import logging
import stats

api_id = 25731065
api_hash = 'be534fb5a5afd8c3308c9ca92afde672'
bot_token = '6865008064:AAHfTdmqXhrd-P-2Og2Mu-I5z9_Rh9WQMCY'

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot
app = Client("mention_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def is_user_admin(chat_id, user_id):
    """Check if a user is an admin or owner of the chat."""
    try:
        chat_member = await app.get_chat_member(chat_id, user_id)
        status = chat_member.status
        logger.info(f"Fetched chat member status: {status} for user_id: {user_id}")
        logger.info(f"Type of status: {type(status)}")

        # Check if the user is an admin or the creator of the chat
        if status in {enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER}:
            return True
        return False
    except Exception as e:
        logger.error(f"Error fetching chat member status for user_id {user_id}: {e}")
        return False

@app.on_message(filters.command("mention") & filters.group)
async def mention(client, message):
    """Handle the /mention command."""
    user_id = message.from_user.id
    chat_id = message.chat.id

    logger.info(f"Chat ID: {chat_id}, User ID: {user_id}")

    # Check if the user is an admin or the chat creator
    is_admin = await is_user_admin(chat_id, user_id)
    logger.info(f"User admin status: {is_admin}")

    if not is_admin:
        await message.reply("You need to be an admin to use this command.")
        return

    # Your logic to handle mentions
    command_parts = message.text.split(maxsplit=1)
    mentions = []

    # Fetch all chat members
    async for member in app.get_chat_members(chat_id):
        # Check if the user is not a bot
        if not member.user.is_bot:
            if member.user.username:
                mentions.append(f"@{member.user.username}")
            else:
                # Use user ID and first name for mention
                mentions.append(f"[{member.user.first_name}](tg://user?id={member.user.id})")

    if len(command_parts) > 1:
        # Extract the custom message from the command
        custom_message = command_parts[1]
        # Create the mention part of the message
        mention_chunks = [", ".join(mentions[i:i + 5]) for i in range(0, len(mentions), 5)]
        for chunk in mention_chunks:
            full_message = f"{custom_message}\n{chunk}"
            await message.reply(full_message)
            await asyncio.sleep(2)  # Wait for 2 seconds between messages
    else:
        # Split mentions into chunks of 5
        mention_chunks = [", ".join(mentions[i:i + 5]) for i in range(0, len(mentions), 5)]
        for chunk in mention_chunks:
            full_message = chunk
            await message.reply(full_message)
            await asyncio.sleep(1)  # Wait for 1 second between messages

@app.on_message(filters.command("dm_msg") & filters.group)
async def dm_msg(client, message):
    chat_id = message.chat.id
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) > 1:
        # Extract the custom message from the command
        custom_message = command_parts[1]

        # Send initial reply message
        reply_message = await message.reply("Getting...")

        # Initialize counters
        failed_count = 0
        done_count = 0

        # Collect user IDs and send private messages
        async for member in app.get_chat_members(chat_id):
            if not member.user.is_bot:
                try:
                    # Send a private message to each user
                    await client.send_message(member.user.id, custom_message)
                    done_count += 1
                    await asyncio.sleep(1)  # To avoid hitting rate limits
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send message to user {member.user.id}: {e}")

        # Update the reply message with the counts
        await reply_message.edit(f"Total members contacted: {done_count + failed_count}\nDone: {done_count}\nFailed: {failed_count}")
    else:
        await message.reply("Usage: /dm_msg <message>")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    # Add user to stats
    stats.add_user(user_id)
    await message.reply("Hello! Use /mention <mention message> in a group to mention all members with a custom message.\nUse /dm_msg <message> in a group to send a custom message to all group members via private message.")

@app.on_message(filters.command("users") & filters.private)
async def users(client, message):
    # Get the user count from stats.py
    user_count = stats.get_user_count()

    # Reply with the user count
    await message.reply(f"Users: {user_count}\nGroups: 0")

@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast(client, message):
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) > 1:
        # Extract the custom message from the command
        broadcast_message = command_parts[1]

        # Get the list of all user IDs
        user_ids = stats.get_all_user_ids()

        # Send the broadcast message to all users
        done_count = 0
        failed_count = 0
        for user_id in user_ids:
            try:
                await client.send_message(user_id, broadcast_message)
                done_count += 1
                await asyncio.sleep(1)  # To avoid hitting rate limits
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast message to user {user_id}: {e}")

        # Send a confirmation message
        await message.reply(f"Broadcast message sent to {done_count} users.\nFailed to send to {failed_count} users.")
    else:
        await message.reply("Usage: /broadcast <message>")

app.run()
