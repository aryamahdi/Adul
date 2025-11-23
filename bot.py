import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("8395891979:AAHK_mrf5wTp8p1mTmz9tq1hecn55dEkhqE")
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Balasan test
        requests.get(URL, params={
            "chat_id": chat_id,
            "text": f"Bot aktif! Kamu mengirim: {text}"
        })

    return {"ok": True}

@app.route('/', methods=['GET'])
def home():
    return "Bot Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
