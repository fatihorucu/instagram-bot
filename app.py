import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Bunları Render panelinden gireceğiz, koda yazmıyoruz.
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Hatalı Doğrulama", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        if data.get('object') == 'instagram':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'comments':
                        comment_id = change['value']['id']
                        user_name = change['value']['from']['username']
                        # Kendi hesabına cevap vermemesi için
                        if user_name != 'mfatihorucu':
                            send_dm(comment_id)
    except: pass
    return "OK", 200

def send_dm(comment_id):
    url = "https://graph.facebook.com/v23.0/me/messages"
    payload = {
        "recipient": {"comment_id": comment_id},
        "message": {"text": "Otomatik Yanıt Sistemimiz Aktif! 🚀"}
    }
    requests.post(url, json=payload, params={"access_token": PAGE_ACCESS_TOKEN})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))