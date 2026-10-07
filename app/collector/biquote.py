from datetime import datetime, timedelta, timezone

import requests

from app.config import BIQUOTE_BASE_URL, BIQUOTE_TIMEOUT


class BiquoteClient:
    def __init__(
        self,
        timeout: int = BIQUOTE_TIMEOUT,
        base_url: str = BIQUOTE_BASE_URL,
    ):
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")

    def get_ohlc(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 100,
        to: str | None = None,
    ) -> list[dict]:
        url = f"{self.base_url}/{symbol}/ohlc"
        params = {
            "interval": interval,
            "limit": limit,
        }

        if to is not None:
            params["to"] = to

        response = requests.get(
            url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError(
                "Invalid API response: expected object"
            )

        bars = data.get("bars")

        if not isinstance(bars, list):
            raise ValueError(
                "Invalid API response: missing bars"
            )

        return bars

    def get_current_open_candle(
        self,
        symbol: str,
        interval: str = "1m",
    ) -> dict | None:
        bars = self.get_ohlc(
            symbol=symbol,
            interval=interval,
            limit=3,
        )

        for bar in bars:
            if bar.get("isOpen") is True:
                return bar

        return None

    def get_latest_candles(
        self,
        symbol: str,
        count: int = 300,
        interval: str = "1m",
    ) -> list[dict]:
        if count <= 0:
            return []

        collected: dict[str, dict] = {}
        to = None

        while len(collected) < count:
            bars = self.get_ohlc(
                symbol=symbol,
                interval=interval,
                limit=min(301, count - len(collected) + 1),
                to=to,
            )

            if not bars:
                break

            previous_count = len(collected)

            for bar in bars:
                open_time = bar.get("openTime")

                if open_time is None:
                    raise ValueError(
                        "Invalid bar: missing openTime"
                    )

                collected[open_time] = bar

                if len(collected) >= count:
                    break

            if len(collected) == previous_count:
                break

            oldest_time = min(collected)

            oldest_dt = datetime.fromisoformat(
                oldest_time.replace("Z", "+00:00")
            )

            to = (
                oldest_dt - timedelta(minutes=1)
            ).astimezone(timezone.utc).isoformat().replace(
                "+00:00",
                "Z",
            )

        bars = sorted(
            collected.values(),
            key=lambda bar: bar["openTime"],
        )

        return bars[-count:]


def is_closed_bar(bar: dict) -> bool:
    return bar.get("isOpen") is False


def bar_to_candle(bar: dict) -> dict:
    required_fields = (
        "openTime",
        "open",
        "high",
        "low",
        "close",
        "tickVolume",
    )

    for field in required_fields:
        if field not in bar:
            raise ValueError(
                f"Invalid bar: missing {field}"
            )

    timestamp = int(
        datetime.fromisoformat(
            bar["openTime"].replace("Z", "+00:00")
        ).timestamp()
    )

    return {
        "time": timestamp,
        "open": float(bar["open"]),
        "high": float(bar["high"]),
        "low": float(bar["low"]),
        "close": float(bar["close"]),
        "tick_volume": int(bar["tickVolume"]),
    }
