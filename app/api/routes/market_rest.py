from fastapi import APIRouter, Query
from app.db.mongo import ticks_collection
from app.schemas.tick import MarketTick

router = APIRouter()

@router.get("/market/latest", response_model=list[MarketTick])
def get_latest_ticks(limit: int = Query(50, le=500)):
    data = list(
        ticks_collection
        .find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return data
