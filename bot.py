import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, add_card, get_cards, delete_card, update_card_paid, delete_all_cards, delete_everything
from datetime import datetime
import threading
from flask import Flask
from telegram.ext import Updater, CommandHandler
import os
import time
import requests
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.error import Conflict
import pytz
from flask import Flask
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

app = Flask(__name__)


@app.route('/')
def index():
    # Gửi thông báo rằng bot đang hoạt động
    return "Bot is running!"


def run():
    # Chạy ứng dụng Flask trên cổng 8080
    app.run(host='0.0.0.0', port=8080)


def start(update, context):
    update.message.reply_text(
        "👋 Dùng /add <tên> <ngày>, /list, /add_list, /delete <tên>, /delete_id, /delete_all để quản lý thẻ."
    )


def add(update, context):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("❗ Dùng: /add <tên_thẻ> <ngày>")
        return
    try:
        name = args[0]
        due_day = int(args[1])
        chat_id = str(update.message.chat_id)
        add_card(name, due_day, chat_id)
        update.message.reply_text(
            f"✅ Đã thêm thẻ {name}, đến hạn ngày {due_day}")
    except:
        update.message.reply_text("⚠️ Lỗi định dạng. Dùng: /add <tên> <ngày>")


def list_cards(update, context):
    chat_id = str(update.message.chat_id)
    cards = get_cards(chat_id)
    if not cards:
        update.message.reply_text("📭 Bạn chưa thêm thẻ nào.")
    else:
        vn_now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
        this_month = vn_now.month
        msg = "💳 Danh sách thẻ:\n"
        for card in cards:
            name = card['name']
            due_day = card['due_day']
            paid_month = card['last_paid_month']
            status = "✅ Đã thanh toán" if paid_month == this_month else "❗Chưa thanh toán"
            msg += f"• {name} – ngày {due_day} ({status})\n"
        update.message.reply_text(msg)


def delete(update, context):
    args = context.args
    if not args:
        update.message.reply_text("❗ Dùng: /delete <tên_thẻ>")
        return
    name = args[0]
    chat_id = str(update.message.chat_id)
    delete_card(name, chat_id)
    update.message.reply_text(f"🗑️ Đã xoá thẻ {name}")


def button(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith("paid:"):
        card_id = data.split(":")[1]
        print("Data", data)
        print("Card", card_id)
        update_card_paid(card_id)
        query.edit_message_text(
            "✅ Đã ghi nhận bạn đã thanh toán thẻ tháng này!")


def add_list(update, context):
    chat_id = str(update.message.chat_id)
    lines = update.message.text.split('\n')[1:]  # Bỏ dòng /add_list
    success = 0
    fail = 0

    for line in lines:
        try:
            name, day = line.rsplit(' ', 1)  # Lấy tên và ngày
            due_day = int(day)
            add_card(name.strip(), due_day, chat_id)
            success += 1
        except:
            fail += 1

    update.message.reply_text(f"✅ Đã thêm {success} thẻ. ⚠️ Lỗi {fail} dòng.")


def delete_id(update, context):
    chat_id = str(update.message.chat_id)
    delete_all_cards(chat_id)
    update.message.reply_text("🗑️ Đã xoá toàn bộ thẻ của bạn.")


def delete_all(update, context):
    admin_id = str(update.message.chat_id)
    # Tuỳ chọn: chỉ cho phép xoá nếu là bạn
    if admin_id != os.getenv("ADMIN_CHAT_ID", ""):
        update.message.reply_text("🚫 Bạn không có quyền thực hiện lệnh này.")
        return

    delete_everything()
    update.message.reply_text("💥 Đã xoá toàn bộ dữ liệu (mọi người).")


def get_chat_id(update, context):

    chat = update.effective_chat
    chat_type = chat.type
    chat_title = chat.title or chat.username or chat.first_name or "Không rõ"
    chat_id = chat.id
    print("Chat Id", chat_id)

    msg = (f"📌 Thông tin chat:\n"
           f"• Type: {chat_type}\n"
           f"• Title/Name: {chat_title}\n"
           f"• Chat ID: `{chat_id}`")
    update.message.reply_text(msg, parse_mode='Markdown')


def run_bot():
    init_db()

    def start_bot():
        updater = Updater(TELEGRAM_TOKEN, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("add", add))
        dp.add_handler(CommandHandler("list", list_cards))
        dp.add_handler(CommandHandler("delete", delete))
        dp.add_handler(CommandHandler("add_list", add_list))
        dp.add_handler(CommandHandler("delete_id", delete_id))
        dp.add_handler(CommandHandler("delete_all", delete_all))
        dp.add_handler(CommandHandler("getid", get_chat_id))
        dp.add_handler(CallbackQueryHandler(button))

        print("🚀 Bot bắt đầu polling...")
        updater.start_polling()
        updater.idle()

    try:
        start_bot()
    except Exception as e:
        print("⚠️ Bot lỗi:", e)
        if "Conflict" in str(e):
            print("⚠️ Conflict phát hiện – gọi deleteWebhook và thử lại...")
            try:
                r = requests.get(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook"
                )
                if r.status_code == 200:
                    print("✅ Đã xoá webhook. Đợi 3s rồi retry...")
                    time.sleep(3)
                    start_bot()
                else:
                    print("❌ deleteWebhook thất bại:", r.text)
            except Exception as ex:
                print("❌ Lỗi khi gọi deleteWebhook:", ex)


if __name__ == "__main__":
    run_bot()
