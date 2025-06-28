import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from datetime import datetime
import pytz
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

# Lấy URL kết nối MongoDB từ biến môi trường
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
db = client.get_database(
    "Cluster0")  # Lấy cơ sở dữ liệu mặc định, bạn có thể thay đổi nếu muốn

# Tạo collection 'cards' (tương đương với bảng trong PostgreSQL)
cards_collection = db.cards


def connect():
    if not MONGO_URL:
        raise ValueError("MONGO_URL is not set.")
    return client


def init_db():
    # MongoDB tự động tạo collection khi bạn insert dữ liệu đầu tiên, không cần phải tạo thủ công.
    pass


def add_card(name, due_day, chat_id):
    card = {
        "name": name,
        "due_day": due_day,
        "chat_id": chat_id,
        "last_paid_month": None  # Mặc định là None
    }
    cards_collection.insert_one(card)


def get_cards(chat_id):
    return list(cards_collection.find({"chat_id": chat_id}).sort("due_day", 1))


def delete_card(name, chat_id):
    cards_collection.delete_one({"name": name, "chat_id": chat_id})


def get_all_cards_for_reminder():
    vn_now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
    this_month = vn_now.month
    day = vn_now.day
    return list(
        cards_collection.find({
            "due_day": {
                "$in": [day, day + 1]
            },
            "$or": [{
                "last_paid_month": None
            }, {
                "last_paid_month": {
                    "$ne": this_month
                }
            }]
        }).sort("due_day", 1))


def update_card_paid(card_id):
    _card_id = ObjectId(card_id)
    vn_now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
    current_month = vn_now.month
    cards_collection.update_one({"_id": _card_id},
                                {"$set": {
                                    "last_paid_month": current_month
                                }})


def delete_all_cards(chat_id):
    cards_collection.delete_many({"chat_id": chat_id})


def delete_everything():
    cards_collection.delete_many({})
