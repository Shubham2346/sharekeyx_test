# Upstox Live Market Data Backend (FastAPI)

A production-ready **FastAPI backend** that consumes **Upstox Market Data Feed (V3)** via WebSockets, decodes Protobuf messages, stores market data in **MongoDB**, and exposes **REST + WebSocket APIs** for frontend integration.

This backend is **frontend-agnostic**, scalable, and designed following real-world backend engineering practices.

---

## 🚀 Features

- Live market data ingestion from **Upstox WebSocket API**
- Protobuf decoding (`MarketDataFeedV3`)
- MongoDB storage for:
  - Raw ticks
  - Live prices
  - 1-minute OHLC candles
- FastAPI REST APIs for frontend consumption
- FastAPI WebSocket endpoint for real-time streaming
- Background services started safely on application startup
- Clean, modular backend architecture

---

## 🏗️ Tech Stack

- **Backend Framework:** FastAPI
- **WebSockets:** `websockets`
- **Database:** MongoDB
- **Protocol:** Protobuf (Upstox MarketDataFeed V3)
- **Runtime:** Python 3.9+
- **ASGI Server:** Uvicorn

---

## 📁 Final Project Structure

```text
upstox_fetch_live/
│
├── app/                            # FastAPI application
│   ├── main.py                     # App entry point
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── health.py           # Health check API
│   │       ├── market_rest.py      # REST APIs
│   │       └── market_ws.py        # WebSocket API
│   │
│   ├── services/
│   │   └── upstox_feed.py          # Background feed orchestration
│   │
│   ├── db/
│   │   └── mongo.py                # MongoDB connection
│   │
│   ├── schemas/                    # API response models
│   │
│   └── core/
│       └── cors.py                 # CORS configuration
│
├── scripts/                        # Market feed logic (standalone)
│   ├── websocket_live_to_mongo.py
│   ├── websocket_live_prices.py
│   ├── websocket_ticks_to_candles.py
│   ├── token_helper.py
│   ├── load_instruments.py
│   ├── MarketDataFeedV3.proto
│   └── MarketDataFeedV3_pb2.py
│
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── README.md
└── complete.json                   # Instruments metadata
