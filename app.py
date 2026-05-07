import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

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
    # --- KRİTİK LOG: Meta'dan gelen her şeyi görmemizi sağlar ---
    print("Meta'dan Gelen Veri:", data) 
    
    if data.get('object') == 'instagram':
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                # Alan ismini kontrol edelim
                field = change.get('field')
                print(f"Değişiklik Alanı: {field}")
                
                if field == 'comments':
                    comment_id = change['value']['id']
                    user_name = change['value']['from']['username']
                    
                    print(f"Yorum Yakalandı! Yazan: {user_name}, ID: {comment_id}")
                    
                    if user_name != 'mfatihorucu':
                        send_dm(comment_id)
    
    return "OK", 200

def send_dm(comment_id):
    # API versiyonunu v19.0 olarak sabitleyelim (En kararlısı)
    url = "https://graph.facebook.com/v19.0/me/messages"
    payload = {
        "recipient": {"comment_id": comment_id},
        "message": {"text": "Otomatik Yanıt Sistemimiz Aktif! 🚀"}
    }
    response = requests.post(url, json=payload, params={"access_token": PAGE_ACCESS_TOKEN})
    print(f"DM Gönderim Durumu: {response.status_code}, Cevap: {response.text}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
