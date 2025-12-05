import uuid
import os
from datetime import datetime
from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "medlens")

def _get_collection():
    client = MongoClient(MONGO_URL)
    return client[DB_NAME].signals


def save_raw_signal(data: bytes, metadata: dict = None):
    meta = metadata or {}
    doc = {
        "_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow(),
        "metadata": meta,
        "blob": data,
    }
    col = _get_collection()
    col.insert_one(doc)
    return doc["_id"]


def init_db():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    # create indexes
    db.signals.create_index([("metadata.patient_id", 1)])
