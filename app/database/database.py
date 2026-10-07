import sqlite3
from pathlib import Path

from app.config import CANDLE_SCHEMA, DATABASE_PATH, DATA_DIR


def connect(database_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(database_path)


def initialize(database_path: Path = DATABASE_PATH) -> None:
    conn = connect(database_path)
    try:
        conn.execute(CANDLE_SCHEMA)
        conn.commit()
    finally:
        conn.close()


def get_candle(
    time: int,
    database_path: Path = DATABASE_PATH,
) -> dict | None:
    conn = connect(database_path)
    try:
        row = conn.execute(
            """
            SELECT
                time,
                open,
                high,
                low,
                close,
                tick_volume
            FROM candles
            WHERE time = ?
            """,
            (time,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return {
        "time": row[0],
        "open": row[1],
        "high": row[2],
        "low": row[3],
        "close": row[4],
        "tick_volume": row[5],
    }


def upsert_candle(
    candle: dict,
    database_path: Path = DATABASE_PATH,
) -> None:
    conn = connect(database_path)
    try:
        conn.execute(
            """
            INSERT INTO candles (
                time,
                open,
                high,
                low,
                close,
                tick_volume,
                spread,
                real_volume
            )
            VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
            ON CONFLICT(time) DO UPDATE SET
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                tick_volume = excluded.tick_volume
            """,
            (
                candle["time"],
                candle["open"],
                candle["high"],
                candle["low"],
                candle["close"],
                candle["tick_volume"],
            ),
        )
        conn.commit()
    finally:
        conn.close()
