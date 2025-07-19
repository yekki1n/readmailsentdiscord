import imaplib
import email
from bs4 import BeautifulSoup
import json
import re

def read_latest_game_email():
    try:
        print("[📥] Đang đọc cấu hình...")
        with open("config.json") as f:
            config = json.load(f)

        gmail_user = config["gmail_user"]
        gmail_pass = config["gmail_app_password"]

        print("[🔐] Đang kết nối Gmail...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_user, gmail_pass)
        mail.select("inbox")

        print("[📨] Đang tìm email Twitch...")
        result, data = mail.search(None, '(FROM "twitch")')
        if result != "OK":
            print("[❌] Không thể tìm email.")
            return []

        mail_ids = data[0].split()
        if not mail_ids:
            print("[❌] Không có email nào khớp.")
            return []

        latest_emails = reversed(mail_ids[-10:])
        print(f"[ℹ️] Đang kiểm tra {len(mail_ids[-10:])} email gần đây...")

        valid_streams = []  # Danh sách để lưu thông tin stream hợp lệ

        for mail_id in latest_emails:
            result, data = mail.fetch(mail_id, "(RFC822)")
            if result != "OK":
                continue

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        html_body = part.get_payload(decode=True).decode()
                        soup = BeautifulSoup(html_body, "html.parser")
                        if contains_game(soup):
                            stream_info = extract_stream_info(soup)
                            if stream_info:
                                valid_streams.append((stream_info, mail_id))  # Lưu cả thông tin và mail_id
            else:
                if msg.get_content_type() == "text/html":
                    html_body = msg.get_payload(decode=True).decode()
                    soup = BeautifulSoup(html_body, "html.parser")
                    if contains_game(soup):
                        stream_info = extract_stream_info(soup)
                        if stream_info:
                            valid_streams.append((stream_info, mail_id))  # Lưu cả thông tin và mail_id

        # Xóa các email đã xử lý
        for _, mail_id in valid_streams:
            mail.store(mail_id, '+FLAGS', '\\Deleted')

        mail.expunge()  # Thực hiện xóa các email đã đánh dấu

        return [info for info, _ in valid_streams]  # Trả về chỉ thông tin stream

    except Exception as e:
        print(f"[❌] Lỗi khi đọc email: {e}")
        return []

def contains_game(soup):
    keywords = ["valorant", "league of legends", "lol", "stream", "live", "playing", "watch", "radiant", "lp", "rr", "rank", "teamfight tactics"]
    for text in soup.find_all(text=True):
        if any(keyword in text.lower() for keyword in keywords):
            return True
    return False

def extract_stream_info(soup):
    try:
        title = soup.title.string if soup.title else ""
        body_text = ' '.join(soup.stripped_strings)

        if any(keyword in title.lower() for keyword in ["valorant", "league of legends", "lol", "radiant", "lp", "rr", "rank", "teamfight tactics"]) or \
           any(keyword in body_text.lower() for keyword in ["valorant", "league of legends", "lol", "radiant", "lp", "rr", "rank", "teamfight tactics"]):

            link_tags = soup.find_all("a", text=re.compile(r"twitch\.tv/[^/]+"))

            for link_tag in link_tags:
                if link_tag.string and "twitch.tv" in link_tag.string:
                    stream_link = link_tag.string.strip()
                    username = stream_link.rstrip("/").split("/")[-1]

                    title_tag = soup.find("strong")
                    stream_title = title_tag.text.strip() if title_tag else "Không có tiêu đề"
                    
                    # Lấy tên game từ thẻ <a>
                    game_tag = soup.find("a", text=re.compile(r"Đang truyền phát .*"))
                    game_name = game_tag.text.split('Đang truyền phát ')[-1].strip() if game_tag else "Không có thông tin game"

                    if username and username != "email-unsubscribe":
                        return f"🔥 {username} đang phát trực tiếp {game_name}: {stream_link} \n{stream_title}"

        print("[🔍] Không tìm thấy thông tin stream.")
        return None

    except Exception as e:
        print(f"[❌] Lỗi khi xử lý HTML: {e}")
        return None