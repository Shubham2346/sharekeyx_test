import json
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["upstox_market"]
col = db["instruments"]

# Load instruments JSON
with open("complete.json", "r", encoding="utf-8") as f:
    data = json.load(f)

docs = []
for item in data:
    docs.append({
        "instrument_key": item["instrument_key"],
        "symbol": item.get("tradingsymbol"),
        "company_name": item.get("name"),
        "exchange": item.get("exchange")
    })

# Clear old data & insert fresh
col.delete_many({})
col.insert_many(docs)

# Create index for fast lookup
col.create_index("instrument_key", unique=True)

print(f"✅ Instruments loaded successfully: {len(docs)} records")
