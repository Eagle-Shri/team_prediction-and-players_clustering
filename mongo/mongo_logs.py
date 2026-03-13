from pymongo import MongoClient
from datetime import datetime
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client[Config.MONGO_DB]
logs = db.activity_logs

def log_activity(user, action):
    logs.insert_one({
        "user": user,
        "action": action,
        "timestamp": datetime.utcnow()
    })
