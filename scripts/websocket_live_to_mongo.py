import asyncio
import json
import ssl
import os
import websockets
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from google.protobuf.json_format import MessageToDict
import MarketDataFeedV3_pb2 as pb

# Load env
load_dotenv()

ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION")

# Mongo connection
mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]
ticks_col = db[COLLECTION_NAME]


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


async def fetch_live_ticks():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    auth = get_market_data_feed_authorize_v3()
    ws_url = auth["data"]["authorized_redirect_uri"]

    async with websockets.connect(
        ws_url,
        ssl=ssl_context,
        ping_interval=20
    ) as ws:

        print("✅ WebSocket connected")

        sub_msg = {
            "guid": "live_ticks",
            "method": "sub",
            "data": {
                "mode": "ltpc",
                "instrumentKeys": [
                    "NSE_INDEX|Nifty 50",
                    "NSE_INDEX|Nifty Bank"
                ]
            }
        }

        await ws.send(json.dumps(sub_msg).encode())
        print("📡 Subscribed to live ticks")

        while True:
            try:
                message = await ws.recv()
                data = decode_protobuf(message)

                record = {
                    "received_at": datetime.utcnow(),
                    "data": data
                }

                ticks_col.insert_one(record)
                print("📥 Tick saved")

            except Exception as e:
                print("❌ Error:", e)


def start_market_feed():
    asyncio.run(fetch_live_ticks())

