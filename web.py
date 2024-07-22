from flask import Flask
from mention import app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
