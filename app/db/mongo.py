from pymongo import MongoClient
from os import getenv

MONGO_URI = getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["market_data"]

ticks_collection = db["ticks"]
candles_collection = db["candles"]
