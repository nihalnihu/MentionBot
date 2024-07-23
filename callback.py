

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if user_id != OWNER_ID:
        await callback_query.answer("You are not authorized to use this command.")
        return

    log_file_path = "bot.log"

    if data == "send_file":
        if os.path.exists(log_file_path):
            await callback_query.message.reply_document(document=log_file_path, caption="Here is the log file.")
        else:
            await callback_query.message.reply_text("Log file does not exist.")

    elif data == "print_text":
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as file:
                log_content = file.read()
            await callback_query.message.reply_text("Here are the latest logs:\n\n" + log_content)
        else:
            await callback_query.message.reply_text("Log file does not exist.")
