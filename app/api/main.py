from fastapi import FastAPI, HTTPException, Query

from app.config import DATABASE_PATH, INTERVAL, SYMBOL
from app.database import (
    get_candle,
    get_candle_count,
    get_candles,
    get_latest_candle,
)

app = FastAPI(
    title="XAUUSD Data Layer API",
    description="Read-only API for XAUUSD market data stored in SQLite.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "xauusd-data-layer",
    }


@app.get("/api/v1/candles")
def candles(
    limit: int = Query(default=100, ge=1, le=1000),
    start_time: int | None = Query(default=None),
    end_time: int | None = Query(default=None),
) -> dict:
    if (
        start_time is not None
        and end_time is not None
        and start_time > end_time
    ):
        raise HTTPException(
            status_code=400,
            detail="start_time must be less than or equal to end_time",
        )

    result = get_candles(
        limit=limit,
        start_time=start_time,
        end_time=end_time,
        database_path=DATABASE_PATH,
    )

    return {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "count": get_candle_count(DATABASE_PATH),
        "returned": len(result),
        "candles": result,
    }


@app.get("/api/v1/candles/latest")
def latest_candle() -> dict:
    candle = get_latest_candle(DATABASE_PATH)

    if candle is None:
        raise HTTPException(
            status_code=404,
            detail="No candles available",
        )

    return {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "candle": candle,
    }


@app.get("/api/v1/candles/{timestamp}")
def candle(timestamp: int) -> dict:
    result = get_candle(
        timestamp,
        database_path=DATABASE_PATH,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Candle not found: {timestamp}",
        )

    return {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "candle": result,
    }


@app.get("/api/v1/price")
def price() -> dict:
    candle = get_latest_candle(DATABASE_PATH)

    if candle is None:
        raise HTTPException(
            status_code=404,
            detail="No candles available",
        )

    return {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "price": candle["close"],
        "time": candle["time"],
    }
