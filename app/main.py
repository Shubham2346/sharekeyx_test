from fastapi import FastAPI
from app.core.cors import setup_cors
from app.api.routes import health, market_rest, market_ws

app = FastAPI(
    title="Upstox Market Data Backend",
    version="1.0.0",
    description="Backend service providing live & historical market data"
)

# Enable CORS for any frontend
setup_cors(app)

# Register API routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(market_rest.router, prefix="/api", tags=["Market"])
app.include_router(market_ws.router)

@app.get("/")
def root():
    return {"status": "Backend is running"}

@app.on_event("startup")
def boot():
    from app.services.upstox_feed import start_feed
    start_feed()
    print("🚀 Market feed started")

