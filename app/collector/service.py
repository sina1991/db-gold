from pathlib import Path

from app.collector.biquote import (
    BiquoteClient,
    bar_to_candle,
    is_closed_bar,
)
from app.config import DATABASE_PATH, INTERVAL, SYMBOL
from app.database import upsert_candle


class CollectorService:
    def __init__(
        self,
        client: BiquoteClient | None = None,
        database_path: Path = DATABASE_PATH,
    ):
        self.client = client or BiquoteClient()
        self.database_path = database_path

    def get_current_open_candle(self) -> dict | None:
        return self.client.get_current_open_candle(
            symbol=SYMBOL,
            interval=INTERVAL,
        )

    def get_current_price(self) -> float | None:
        candle = self.get_current_open_candle()

        if candle is None:
            return None

        return float(candle["close"])

    def collect_latest_closed(self) -> dict | None:
        bars = self.client.get_ohlc(
            symbol=SYMBOL,
            interval=INTERVAL,
            limit=3,
        )

        for bar in bars:
            if not is_closed_bar(bar):
                continue

            candle = bar_to_candle(bar)

            upsert_candle(
                candle,
                database_path=self.database_path,
            )

            return candle

        return None

    def collect_initial(self, count: int = 300) -> list[dict]:
        if count <= 0:
            return []

        bars = self.client.get_latest_candles(
            symbol=SYMBOL,
            count=count + 1,
            interval=INTERVAL,
        )

        candles = []

        for bar in bars:
            if not is_closed_bar(bar):
                continue

            candle = bar_to_candle(bar)

            upsert_candle(
                candle,
                database_path=self.database_path,
            )

            candles.append(candle)

        return candles
