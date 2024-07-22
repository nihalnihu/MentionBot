from flask import Flask
import threading
import mention  # Import your bot module here

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

def run_flask():
    app.run(host='0.0.0.0', port=8000)

def run_bot():
    mention.run_bot()  # Replace with the function to start your bot

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
