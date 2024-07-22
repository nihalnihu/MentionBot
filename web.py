from flask import Flask
import threading
import os
from pyrogram import Client
import logging
import signal
import sys

# Initialize Flask app
flask_app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
flask_app.logger.setLevel(logging.INFO)

# Initialize Pyrogram client
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@flask_app.route('/health', methods=['GET'])
def health_check():
    bot_status = "running" if app.is_running() else "not running"
    return f"Flask and bot status: {bot_status}", 200

def run_flask_app():
    port = int(os.getenv('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

def run_pyrogram_bot():
    try:
        app.run()
    except Exception as e:
        flask_app.logger.error(f"An error occurred with Pyrogram: {e}")

def signal_handler(sig, frame):
    print('Signal received, shutting down...')
    app.stop()  # Gracefully stop the Pyrogram bot
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    # Run Flask app in a separate thread
    threading.Thread(target=run_flask_app).start()
    # Start Pyrogram bot
    run_pyrogram_bot()
