import asyncio
import json
import ssl
import os
import websockets
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from pymongo import MongoClient
from dotenv import load_dotenv
from google.protobuf.json_format import MessageToDict
import MarketDataFeedV3_pb2 as pb

# Load env
load_dotenv()

ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

mongo = MongoClient(MONGO_URI)
db = mongo["upstox_market"]

ticks_col = db["ticks"]
candles_1m = db["candles_1m"]

# In-memory candle store
current_candles = {}

def get_minute(ts):
    return ts.replace(second=0, microsecond=0)

def get_market_data_feed_authorize_v3():
    url = "https://api.upstox.com/v3/feed/market-data-feed/authorize"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def decode_protobuf(buffer):
    feed = pb.FeedResponse()
    feed.ParseFromString(buffer)
    return MessageToDict(feed, preserving_proto_field_name=True)

def update_1m_candle(symbol, price, ts):
    minute = get_minute(ts)

    key = (symbol, minute)

    if key not in current_candles:
        current_candles[key] = {
            "symbol": symbol,
            "interval": "1m",
            "start_time": minute,
            "open": price,
            "high": price,
            "low": price,
            "close": price
        }
    else:
        candle = current_candles[key]
        candle["high"] = max(candle["high"], price)
        candle["low"] = min(candle["low"], price)
        candle["close"] = price

    # Close previous minute candle
    for k in list(current_candles.keys()):
        sym, start = k
        if sym == symbol and start < minute:
            candles_1m.insert_one(current_candles.pop(k))

async def fetch_and_build_candles():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    auth = get_market_data_feed_authorize_v3()
    ws_url = auth["data"]["authorized_redirect_uri"]

    async with websockets.connect(ws_url, ssl=ssl_context) as ws:
        print("✅ WebSocket connected")

        sub_msg = {
            "guid": "candles",
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
        print("📡 Subscribed")

        while True:
            msg = await ws.recv()
            data = decode_protobuf(msg)

            now = datetime.utcnow()

            feeds = data.get("feeds", {})
            for symbol, val in feeds.items():
                if "ltpc" in val:
                    ltp = val["ltpc"]["ltp"]

                    ticks_col.insert_one({
                        "symbol": symbol,
                        "price": ltp,
                        "time": now
                    })

                    update_1m_candle(symbol, ltp, now)

def start_candle_builder():
    asyncio.run(fetch_and_build_candles())

