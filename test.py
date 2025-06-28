
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

import requests

ip = requests.get('https://api.ipify.org').text
print(f'Your public IP is: {ip}')


# Lấy URL kết nối MongoDB từ biến môi trường
MONGO_URL = os.getenv("MONGO_URL")

uri = "mongodb+srv://phuocquocnguyen:<db_password>@cluster0.pfcnsne.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(MONGO_URL, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)