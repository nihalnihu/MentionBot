from pyrogram import Client, filters, enums
import asyncio
import logging
import stats
import os
import threading
import subprocess
from flask import Flask
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, CallbackQuery
from stats import check_subscription
from database import add_user, add_group, all_users, all_groups, users, remove_user, already_db, get_all_group_ids

# Environment Variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize Flask
bot = Flask(__name__)

@bot.route('/')
def hello_world():
    return 'Hello, World!'

@bot.route('/health')
def health_check():
    return 'Healthy', 200

def run_flask():
    bot.run(host='0.0.0.0', port=8080)

# Initialize Pyrogram Client
app = Client("TGBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("restart") & filters.private & filters.user(OWNER_ID))
async def update_and_restart(client, message):
    # Notify the user that the update process has started
    response = await message.reply_text("Updating and restarting the bot...")

     # Call the Bash script
    subprocess.Popen(["/bin/bash", "restart.sh"])
    
    # Optionally, delete the initial message to clean up the chat
    await response.delete()

    # Notify the user that the bot is being updated
    await message.reply_text("Bot is being updated and will restart shortly.")


    
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

PM_START = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton('Start Me ▶️', url='https://t.me/TG_GroupMentionBot?start=start')
    ]]
)

@app.on_message(filters.command("mention") & filters.group)
async def mention(client, message):
    user = message.from_user
    chat = message.chat
    mention = user.mention
    if not already_db(user.id):
        GOM_PM = await message.reply_text(
            text=f"Hey {mention}❗ First Start Me In PM",
            reply_markup=PM_START
        )

        await asyncio.sleep(60)
        await GOM_PM.delete()
        await message.delete()
        return
        
    add_group(chat.id)
    
    
    logger.info(f"Chat ID: {chat.id}, User ID: {user.id}")

    is_admin = await is_user_admin(chat.id, user.id)
    logger.info(f"User admin status: {is_admin}")

    if not is_admin:
        await message.delete()
        return

    command_parts = message.text.split(maxsplit=1)
    mentions = []

    async for member in app.get_chat_members(chat.id):
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
    mention = message.from_user.mention
    failed_count = 0
    done_count = 0
    
    if not already_db(user_id):
        GO_PM = await message.reply_text(
            text=f"Hey {mention}❗ First Start Me In PM\n\nDelete In [60](https://t.me/TG_GroupMentionBot?stats=start) Seconds",
            reply_markup=PM_START
        )
        await asyncio.sleep(60)
        await GO_PM.delete()
        await message.delete()
        return
        
    add_group(chat_id)

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

        await reply_message.edit(f"Type: {media_type}\nTotal Members: {done_count + failed_count}\n\nSuccess {done_count}\nFailed: {failed_count}")

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

            await reply_message.edit(f"Type: Text\nTotal Members: {done_count + failed_count}\n\nSuccess: {done_count}\nFailed: {failed_count}")

        else:
            await message.reply("Use: /broadcast <message> or reply to a photo, video, or sticker")



@app.on_message(filters.command("bc") & filters.private & filters.user(OWNER_ID))
async def broadcast_to_all_users(client, message):
    command_parts = message.text.split(maxsplit=1)
    failed_count = 0
    done_count = 0

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

        user_ids = stats.get_all_user_ids()
        for user_id in user_ids:
            try:
                if media_type == "photo":
                    if caption and reply_markup:
                        await client.send_photo(user_id, media[0], caption=media[1], reply_markup=reply_markup)
                    elif caption:
                        await client.send_photo(user_id, media[0], caption=media[1])
                    elif reply_markup:
                        await client.send_photo(user_id, media[0], reply_markup=reply_markup)
                    else:
                        await client.send_photo(user_id, media[0])
                elif media_type == "video":
                    if caption and reply_markup:
                        await client.send_video(user_id, media[0], caption=media[1], reply_markup=reply_markup)
                    elif caption:
                        await client.send_video(user_id, media[0], caption=media[1])
                    elif reply_markup:
                        await client.send_video(user_id, media[0], reply_markup=reply_markup)
                    else:
                        await client.send_video(user_id, media[0])
                elif media_type == "sticker":
                    if reply_markup:
                        await client.send_sticker(user_id, media[0], reply_markup=reply_markup)
                    else:
                        await client.send_sticker(user_id, media[0])
                elif media_type == "text":
                    if reply_markup:
                        await client.send_message(user_id, media[0], reply_markup=reply_markup)
                    else:
                        await client.send_message(user_id, media[0])
                done_count += 1
                await asyncio.sleep(1)  # To avoid hitting rate limits
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send {media_type} to user {user_id}: {e}")

        await reply_message.edit(f"Type: {media_type}\n\nTotal Users: {done_count + failed_count}\nSuccess: {done_count}\nFailed: {failed_count}")
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

            await reply_message.edit(f"Type: Text\n\nTotal Users: {done_count + failed_count}\nSuccess: {done_count}\nFailed: {failed_count}")
        else:
            await message.reply("Use: /bc <message> or reply to a photo, video, or sticker")


START_BTN = [
    [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url="https://t.me/TG_GRPMentionBot?startgroup=true")],

    [InlineKeyboardButton("Help ⚠︎", callback_data="HELP"),
    InlineKeyboardButton("Developer ★", url="t.me/nihh_alll")],
    
    [InlineKeyboardButton("Updates Channel ✔︎", url="t.me/TG_BotCreator")]
]

HELP_MSG = """ 

ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ᴜsᴇ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☺︎︎

✍️ ɢʀᴏᴜᴘ ᴄᴏᴍᴍᴀɴᴅs:

/mention (ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs) - ᴍᴇɴᴛɪᴏɴ ᴀʟʟ ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs. sᴇɴᴅ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴀʟᴏɴᴇ ᴏʀ ʏᴏᴜ ᴄᴀɴ sᴇᴛ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ᴍᴇɴᴛɪᴏɴ 

ᴇɢ:- /mention Halo Guys

/broadcast (ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs) - sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs (ᴘʀɪᴠᴀᴛʟʏ)

ᴇɢ:- /broadcast Halo Guys

‌ｏｒ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴘᴏsᴛs. 

❕sᴜᴘᴘᴏʀᴛᴇᴅ:

ᴛᴇxᴛs, ᴘʜᴏᴛᴏs, ᴠɪᴅᴇᴏs, sᴛɪᴄᴋᴇʀs.

ᴀɴᴅ ᴀʟʟ ᴡɪᴛʜ ʙᴜᴛᴛᴏɴ ᴀɴᴅ ᴄᴀᴘᴛᴏɴ!

ᴇɴᴊᴏʏ🤩
"""

HELP_BTN =  [[
    InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url="https://t.me/TG_GRPMentionBot?startgroup=true")
    ],[
        InlineKeyboardButton("🚫 Close", callback_data="CLOSE")
    ]
    ]
            

START_TXT = """
ʜʏ {},👋

ᴛʜɪs ɪs ᴀ ᴍᴇɴᴛɪᴏɴ ʙᴏᴛ. ɪɴ ᴛʜɪs ʙᴏᴛ ʏᴏᴜ ᴄᴀɴ ᴍᴇɴᴛɪᴏɴ ᴀʟʟ ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs ᴀɴᴅ ᴀʟsᴏ ʏᴏᴜ ᴄᴀɴ sᴇɴᴅ ᴀ ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs ɪɴ ᴘʀɪᴠᴀᴛᴇ.

ᴄʟɪᴄᴋ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ!!

"""

FSUB_MSG = """
Hᴇʏ {}!

Pʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ !㋛︎

"""

FSUB_BTN = [[
    InlineKeyboardButton('❗Join Now ❗', url='t.me/TG_BotCreator')
],[
    InlineKeyboardButton('Try Again', url='https://t.me/TG_GroupMentionBot?start=start')
    
]
           
           ]

STATS_BTN = [
    [
        InlineKeyboardButton('User', callback_data='users'),
        InlineKeyboardButton('Group', callback_data='groups')
    ]
]
             

G_U_BTN = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton('Back', callback_data='stats'),
        InlineKeyboardButton('Close', callback_data='CLOSE')
    ]]
)


@app.on_message(filters.command("start") & filters.group)
def startt(client, gstart):
    gstart.delete()   
    
@app.on_message(filters.command("stats") & filters.group)
def startt(client, gstats):
    gstats.delete()

@app.on_message(filters.command("restart") & filters.group)
def startt(client, grestart):
    grestart.delete()

@app.on_message(filters.command("start") & filters.private)
async def startt(client, start):
    user_id = start.from_user.id
    username = start.from_user.mention
    is_subscribed = await check_subscription(client, user_id)
    print(f"User subscribed: {is_subscribed}")

    if is_subscribed:
        add_user(user_id)
        await start.reply_text(
            text=START_TXT.format(username),
            reply_markup=InlineKeyboardMarkup(START_BTN)
        )
        
    else:
        FS = await start.reply_text(
            text=FSUB_MSG.format(username),
            reply_markup=InlineKeyboardMarkup(FSUB_BTN)
                                     )
        await asyncio.sleep(60)
        await start.delete()
        await FS.delete()




@app.on_callback_query()
async def callback(client, query):
    data = query.data

    if data == 'users':
        user_records = users.find({})
        user_list = []
        for user in user_records:
            user_id = user.get('user_id')
            try:
                user_profile = await client.get_users(user_id)
                username = user_profile.username
                first_name = user_profile.first_name
                if username:
                    # Format link using username
                    user_list.append(f"[{username}](https://t.me/{username})")
                else:
                    # Use user ID link (non-clickable outside Telegram)
                    user_list.append(f"{first_name} (tg://user?id={user_id})")
            except Exception as e:
                # Log detailed error
                print(f"Error fetching profile for User ID {user_id}: {e}")
                user_list.append(f"User ID {user_id} (Error fetching profile)")

        user_text = '\n\n'.join(user_list) or "No users found."
        await query.message.edit_text(
            text=user_text,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=G_U_BTN
        )
    
    elif data == 'groups':
        group_ids = get_all_group_ids()
        group_list = []
        for chat_id in group_ids:
            try:
                chat = await client.get_chat(chat_id)
                username = chat.username
                first_name = chat.title
                if username:
                    # Format link using username
                    group_list.append(f"[@{username}](https://t.me/{username})")
                else:
                    # Display group name
                    group_list.append(f"{first_name} - (Private Group)")
            except Exception as e:
                # Log detailed error
                print(f"Error fetching info for Group ID {chat_id}: {e}")
                group_list.append(f"Group ID {chat_id} (Error fetching info)")

        group_text = '\n\n'.join(group_list) or "No groups found."
        await query.message.edit_text(
            text=group_text, 
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=G_U_BTN
        )

    
    elif data == 'HELP':
        await client.send_chat_action(
            chat_id=query.message.chat.id,
            action=enums.ChatAction.TYPING
        )
        await asyncio.sleep(.5)
        
        await query.message.edit_text(
            text=HELP_MSG,
            reply_markup=InlineKeyboardMarkup(HELP_BTN)
        
        )
        

    elif data == 'CLOSE':
            await query.message.delete()

    elif data == 'STATS_BACK':
        await query.edit_message_text(text=f"Stats for {app.me.mention}\n🙋‍♂️ Users : {ALL_USERS}\n👥 Groups : {ALL_GROUPS}",
                                      reply_markup=InlineKeyboardMarkup(STATS_BTN)
                                     )

    elif query.data == 'stats':
        ALL_USERS = all_users()
        ALL_GROUPS = all_groups()
    
        await query.edit_message_text(
            text=f"Stats for {client.me.mention}\n🙋‍♂️ Users : {ALL_USERS}\n👥 Groups : {ALL_GROUPS}"
        )

@app.on_message(filters.command("stats") & filters.private & filters.user(OWNER_ID))
async def stats(client, message):
    
    await message.reply_text(
        text=f"Stats for {client.me.mention}\n🙋‍♂️ Users : {ALL_USERS}\n👥 Groups : {ALL_GROUPS}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('User', callback_data='users'),
             InlineKeyboardButton('Group', callback_data='groups')]
        ])
    )




@app.on_message(filters.command("group_bc") & filters.private & filters.user(OWNER_ID))
async def broadcast_to_all_groups(client: Client, message):
    command_parts = message.text.split(maxsplit=1)
    failed_count = 0
    done_count = 0

    if message.reply_to_message:
        replied_message = message.reply_to_message
        reply_markup = replied_message.reply_markup
        text = replied_message.text or ""
        caption = replied_message.caption or ""

        # Determine media type and content
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

        group_ids = get_all_group_ids()  # Fetch group IDs from the database
        for group_id in group_ids:
            try:
                if media_type == "photo":
                    await client.send_photo(
                        group_id,
                        media[0],
                        caption=media[1] if media[1] else None,
                        reply_markup=reply_markup
                    )
                elif media_type == "video":
                    await client.send_video(
                        group_id,
                        media[0],
                        caption=media[1] if media[1] else None,
                        reply_markup=reply_markup
                    )
                elif media_type == "sticker":
                    await client.send_sticker(
                        group_id,
                        media[0],
                        reply_markup=reply_markup
                    )
                elif media_type == "text":
                    await client.send_message(
                        group_id,
                        media[0],
                        reply_markup=reply_markup
                    )
                done_count += 1
                await asyncio.sleep(1)  # To avoid hitting rate limits
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send {media_type} to group {group_id}: {e}")

        # Check if the message content has changed before editing
        current_text = reply_message.text
        new_text = f"Type: {media_type.capitalize()}\n\nTotal Groups: {done_count + failed_count}\nSuccess: {done_count}\nFailed: {failed_count}"
        if current_text != new_text:
            await reply_message.edit(new_text)
    else:
        if len(command_parts) > 1:
            custom_message = command_parts[1]
            reply_message = await message.reply("Broadcasting text message...")

            group_ids = get_all_group_ids()  # Fetch group IDs from the database
            for group_id in group_ids:
                try:
                    await client.send_message(group_id, custom_message)
                    done_count += 1
                    await asyncio.sleep(1)
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send message to group {group_id}: {e}")

            # Check if the message content has changed before editing
            current_text = reply_message.text
            new_text = f"Type: Text\n\nTotal Groups: {done_count + failed_count}\nSuccess: {done_count}\nFailed: {failed_count}"
            if current_text != new_text:
                await reply_message.edit(new_text)
        else:
            await message.reply("Use: /group_bc <message> or reply to a photo, video, or sticker")


# Start the Flask server in a separate thread
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    
    # Start the Pyrogram Client
    app.run()
