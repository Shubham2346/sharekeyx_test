from fastapi import WebSocket, APIRouter
import asyncio
from app.db.mongo import ticks_collection

router = APIRouter()

@router.websocket("/ws/market")
async def market_stream(websocket: WebSocket):
    await websocket.accept()

    while True:
        tick = ticks_collection.find_one(
            sort=[("timestamp", -1)],
            projection={"_id": 0}
        )
        if tick:
            await websocket.send_json(tick)
        await asyncio.sleep(1)
