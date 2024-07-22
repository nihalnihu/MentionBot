from flask import Flask, request
from pyrogram import Client
import asyncio
import os

app = Flask(__name__)

api_id = os.getenv('API_ID', '')
api_hash = os.getenv('API_HASH', '')
bot_token = os.getenv('BOT_TOKET', '')

bot = Client("mention_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.route('/')
def index():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Handle incoming webhook data here
    return "Webhook received!", 200

@app.route('/start_bot')
def start_bot():
    asyncio.run(bot.start())
    return "Bot started!", 200

@app.route('/stop_bot')
def stop_bot():
    asyncio.run(bot.stop())
    return "Bot stopped!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
