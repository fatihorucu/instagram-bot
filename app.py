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
    # Bu satır sayesinde ne gelirse gelsin logda göreceğiz
    print("GELEN VERİ YAPISI:", data.keys()) 
    
    if data.get('object') == 'instagram':
        for entry in data.get('entry', []):
            # Eğer Meta YORUM gönderirse burası çalışır
            if 'changes' in entry:
                for change in entry.get('changes', []):
                    if change.get('field') == 'comments':
                        comment_id = change['value']['id']
                        user_name = change['value']['from']['username']
                        print(f"EVET! Yorum yakalandı: {user_name}")
                        if user_name != 'mfatihorucu':
                            send_dm(comment_id)
            
            # Eğer Meta DM gönderirse (senin loglarındaki gibi) burası çalışır
            elif 'messaging' in entry:
                print("DİKKAT: Meta yorum yerine DM verisi gönderdi. Webhook ayarlarını kontrol et!")

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
