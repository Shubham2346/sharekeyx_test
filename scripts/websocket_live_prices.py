import asyncio
import json
import ssl
import os
import websockets
import requests
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from google.protobuf.json_format import MessageToDict
import MarketDataFeedV3_pb2 as pb

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()
ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# -------------------------------------------------
# MONGO
# -------------------------------------------------
client = MongoClient(MONGO_URI)
db = client["upstox_market"]

instruments_col = db["instruments"]
live_prices_col = db["live_prices"]

# -------------------------------------------------
# PICK INSTRUMENTS (SAFE & GUARANTEED)
# -------------------------------------------------
cursor = instruments_col.find(
    {"exchange": "NSE"},
    {"instrument_key": 1, "symbol": 1, "company_name": 1}
).limit(10)   # 🔁 increase later if needed

TRACK_KEYS = []
META_MAP = {}

for doc in cursor:
    key = doc["instrument_key"]
    TRACK_KEYS.append(key)
    META_MAP[key] = {
        "symbol": doc.get("symbol", key),
        "company_name": doc.get("company_name", "Unknown")
    }

if not TRACK_KEYS:
    raise RuntimeError("❌ No instruments found to subscribe")

print("📡 Tracking instruments:", TRACK_KEYS)

# -------------------------------------------------
# UPSTOX AUTH
# -------------------------------------------------
def get_market_data_feed_authorize_v3():
    url = "https://api.upstox.com/v3/feed/market-data-feed/authorize"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

def decode_protobuf(buffer):
    feed = pb.FeedResponse()
    feed.ParseFromString(buffer)
    return MessageToDict(feed, preserving_proto_field_name=True)

# -------------------------------------------------
# LIVE PRICE LOOP
# -------------------------------------------------
async def fetch_live_prices():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    auth = get_market_data_feed_authorize_v3()
    ws_url = auth["data"]["authorized_redirect_uri"]

    async with websockets.connect(ws_url, ssl=ssl_context, ping_interval=20) as ws:
        print("✅ WebSocket connected")

        sub_msg = {
            "guid": "live_prices",
            "method": "sub",
            "data": {
                "mode": "ltpc",
                "instrumentKeys": TRACK_KEYS
            }
        }

        await ws.send(json.dumps(sub_msg).encode())
        print("📡 Subscribed to live prices")

        while True:
            msg = await ws.recv()
            data = decode_protobuf(msg)

            feeds = data.get("feeds", {})
            for key, val in feeds.items():
                ltpc = val.get("ltpc")
                if not ltpc:
                    continue

                ltp = ltpc.get("ltp") or ltpc.get("last_price")
                if ltp is None:
                    continue

                meta = META_MAP.get(key, {})

                live_prices_col.update_one(
                    {"instrument_key": key},
                    {"$set": {
                        "instrument_key": key,
                        "symbol": meta.get("symbol", key),
                        "company_name": meta.get("company_name", "Unknown"),
                        "ltp": ltp,
                        "updated_at": datetime.utcnow()
                    }},
                    upsert=True
                )

                print(meta.get("symbol", key), "→", ltp)

# -------------------------------------------------
# RUN
# -------------------------------------------------
def start_live_prices():
    asyncio.run(fetch_live_prices())

