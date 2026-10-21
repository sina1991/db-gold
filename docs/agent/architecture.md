# Architecture

## Data flow
Biquote HTTP API -> `BiquoteClient` -> `CollectorService`
-> `CollectorRuntime` -> SQLite `candles` table -> FastAPI consumers.

The collector polls every `COLLECTOR_POLL_SECONDS` (configured as 5).
It stores closed bars; `upsert_candle` inserts or updates by candle timestamp.

## Main modules
- `app/config.py`: project paths, symbol/interval, upstream URL, timeout,
  polling interval, and SQLite table DDL.
- `app/collector/biquote.py`: HTTP client, bar pagination, closed-bar check,
  and conversion from upstream bar to internal candle.
- `app/collector/service.py`: collection orchestration and persistence.
- `app/bootstrap/collector_runtime.py`: polling loop and error logging.
- `app/database/database.py`: SQLite connections and candle queries/writes.
- `app/api/main.py`: read-only HTTP endpoints.
- `systemd/*.service`: production process definitions.

## Important behavior
- API candle timestamps are Unix seconds.
- `/api/v1/candles` supports inclusive `start_time` and `end_time` filters.
  Results are returned oldest-to-newest, limited to at most 1000 rows.
- `/api/v1/price` returns the `close` of the latest stored candle. It does
  not call the collector's current-open-candle method.
- The collector's `get_current_price` exists but is not used by the API.
- `collect_initial` exists for historical backfill; the runtime loop calls
  `collect_latest_closed`.

## Runtime and network
Systemd units:
- `xauusd-data-layer-api.service`
- `xauusd-data-layer-collector.service`

The observed API listener was `0.0.0.0:8000`, which binds all IPv4
interfaces. Verify firewall/network policy before assuming the API is private.
