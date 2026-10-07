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
                tick_volume,
                spread,
                real_volume
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
        "spread": row[6],
        "real_volume": row[7],
    }


def get_candles(
    limit: int = 100,
    start_time: int | None = None,
    end_time: int | None = None,
    database_path: Path = DATABASE_PATH,
) -> list[dict]:
    if limit <= 0:
        return []

    query = """
        SELECT
            time,
            open,
            high,
            low,
            close,
            tick_volume,
            spread,
            real_volume
        FROM candles
    """
    conditions = []
    parameters: list[int] = []

    if start_time is not None:
        conditions.append("time >= ?")
        parameters.append(start_time)

    if end_time is not None:
        conditions.append("time <= ?")
        parameters.append(end_time)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY time DESC LIMIT ?"
    parameters.append(limit)

    conn = connect(database_path)
    try:
        rows = conn.execute(query, parameters).fetchall()
    finally:
        conn.close()

    rows.reverse()

    return [
        {
            "time": row[0],
            "open": row[1],
            "high": row[2],
            "low": row[3],
            "close": row[4],
            "tick_volume": row[5],
            "spread": row[6],
            "real_volume": row[7],
        }
        for row in rows
    ]


def get_latest_candle(
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
                tick_volume,
                spread,
                real_volume
            FROM candles
            ORDER BY time DESC
            LIMIT 1
            """
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
        "spread": row[6],
        "real_volume": row[7],
    }


def get_candle_count(
    database_path: Path = DATABASE_PATH,
) -> int:
    conn = connect(database_path)
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM candles"
        ).fetchone()
    finally:
        conn.close()

    return int(row[0])
    

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
