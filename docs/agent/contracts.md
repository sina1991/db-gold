# Data and API Contracts

## Candle model
SQLite table: `candles`

| Field | Type | Constraint / meaning |
|---|---|---|
| `time` | INTEGER | Primary key; Unix timestamp in seconds |
| `open` | REAL | Required |
| `high` | REAL | Required |
| `low` | REAL | Required |
| `close` | REAL | Required |
| `tick_volume` | INTEGER | Nullable |
| `spread` | INTEGER | Nullable |
| `real_volume` | INTEGER | Nullable |

`upsert_candle` inserts by `time`; on conflict it updates OHLC and
`tick_volume`. It sets `spread` and `real_volume` to NULL on insert.

## HTTP endpoints
All application endpoints are GET and read-only.

| Endpoint | Behavior |
|---|---|
| `/health` | Service health response |
| `/api/v1/price` | Latest stored candle close and timestamp |
| `/api/v1/candles/latest` | Latest stored candle |
| `/api/v1/candles/{timestamp}` | Candle for exact Unix timestamp; 404 if absent |
| `/api/v1/candles` | Candle list with optional filters |

`GET /api/v1/candles` parameters:
- `limit`: default 100; allowed 1..1000
- `start_time`: optional inclusive Unix timestamp in seconds
- `end_time`: optional inclusive Unix timestamp in seconds
- If both are present and `start_time > end_time`, returns HTTP 400.
- Response includes `symbol`, `interval`, total database `count`,
  number `returned`, and `candles`.

Missing latest candle returns HTTP 404 on `/api/v1/price` and
`/api/v1/candles/latest`.

FastAPI also exposes its generated OpenAPI/Swagger documentation.
