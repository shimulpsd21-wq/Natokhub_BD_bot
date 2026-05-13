from flask import Flask, send_from_directory, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Natokhub Bot Server Running ✅"

@app.route('/ad')
def ad_page():
    return send_from_directory('webapp', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
