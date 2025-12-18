import threading
from scripts.websocket_live_to_mongo import start_market_feed
from scripts.websocket_live_prices import start_live_prices
from scripts.websocket_ticks_to_candles import start_candle_builder

def start_feed():
    threading.Thread(target=start_market_feed, daemon=True).start()
    threading.Thread(target=start_live_prices, daemon=True).start()
    threading.Thread(target=start_candle_builder, daemon=True).start()
