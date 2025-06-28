import os
import pytz
from datetime import datetime
import requests
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_all_cards_for_reminder

from dotenv import load_dotenv
load_dotenv()

def send_reminder():
    print("📨 Đang gửi reminder...")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    REMIND_HOURS = os.getenv("REMIND_HOURS") or [14]
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now_vn = datetime.now(vietnam_tz)
    hour = now_vn.hour
    if hour in REMIND_HOURS:
        bot = Bot(token=TELEGRAM_TOKEN)
        for card in get_all_cards_for_reminder():
            card_id = card['_id']
            name = card['name']
            due_day = card['due_day']
            chat_id = int(card['chat_id'])
            msg = (
                f"🔔 Nhắc thanh toán (còn 1 ngày)\n"
                f"💳 Thẻ: {name}\n"
                f"📅 Đến hạn: ngày {due_day} tháng này\n"
                f"⏳ Nhớ thanh toán đúng hạn nha!"
            )
            buttons = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Đã thanh toán", callback_data=f"paid:{card_id}")
            ]])
            bot.send_message(chat_id=chat_id, text=msg, reply_markup=buttons)
        print("✅ Reminder đã gửi xong.")

if __name__ == "__main__":
    send_reminder()
