import time
import json
import requests
from datetime import datetime
from email_reader import read_latest_game_email

def send_to_discord(message_html):
    try:
        with open("config.json") as f:
            config = json.load(f)

        webhook_url = config["webhook_url"]
        data = {
            "content": "🔔 Streamer đang live!",
            "embeds": [
                {
                    "title": "Thông báo từ Twitch",
                    "description": message_html[:4000],
                    "color": 16737792
                }
            ]
        }
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            print(f"[❗] Discord webhook failed: {response.status_code} - {response.text}")
        else:
            print(f"[✅] Đã gửi thông báo: {message_html}")
    except Exception as e:
        print(f"[❌] Gửi Discord thất bại: {e}")

def main_loop():
    last_sent = ""
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[⏱] Kiểm tra lúc {now}...")

        html_msg = read_latest_game_email() # Doc lấy email mới nhất có thông tin về game
        if html_msg:
            print("[📧] Có email hợp lệ.")
            if html_msg != last_sent:
                print("[🚀] Gửi Discord...")
                send_to_discord(html_msg)
                last_sent = html_msg
            else:
                print("[🔁] Email đã gửi rồi, không gửi lại.")
        else:
            print("[ℹ️] Không tìm thấy email có thông tin về game.")

        time.sleep(120)

if __name__ == "__main__":
    main_loop()