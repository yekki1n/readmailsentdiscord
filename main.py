import time
import json
import requests
from datetime import datetime
from email_reader import read_latest_game_email

def send_to_discord(messages):
    try:
        with open("config.json") as f:
            config = json.load(f)

        webhook_url = config["webhook_url"]
        
        for message_html in messages:
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
                log_to_file(f"\n\n[✅] Đã gửi thông báo: {message_html}")

    except Exception as e:
        print(f"[❌] Gửi Discord thất bại: {e}")

def log_to_file(log_message):
    try:
        with open("log.txt", "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp} - {log_message}\n")
    except Exception as e:
        print(f"[❌] Lỗi khi ghi log: {e}")

def main_loop():
    last_sent = set()
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[⏱] Kiểm tra lúc {now}...")

        html_msgs = read_latest_game_email()
        if html_msgs:
            print("[📧] Có email hợp lệ.")
            new_msgs = [msg for msg in html_msgs if msg not in last_sent]
            if new_msgs:
                print("[🚀] Gửi Discord...")
                send_to_discord(new_msgs)
                last_sent.update(new_msgs)
            else:
                print("[🔁] Không có thông báo mới để gửi.")
        else:
            print("[ℹ️] Không tìm thấy email có thông tin về game.")

        time.sleep(60)

if __name__ == "__main__":
    main_loop()