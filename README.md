# XAUUSD Data Layer

Independent XAUUSD 1-minute market data layer.

This project collects XAUUSD market data, stores it in SQLite, and exposes the stored data through a read-only HTTP API.

The project is independent from the legacy `/root/metatrader` project.

---

## 1. Installation

### One-line installation

```bash
cd /root/xauusd_data_layer && python3 -m venv .venv && /root/xauusd_data_layer/.venv/bin/pip install -r requirements.txt && /root/xauusd_data_layer/.venv/bin/python -c "from app.database import initialize; initialize()"
```


Project path:

```text
/root/xauusd_data_layer

Enter the project:

cd /root/xauusd_data_layer

Create the virtual environment:

python3 -m venv .venv

Activate it:

source /root/xauusd_data_layer/.venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Initialize the database:

python -c "from app.database import initialize; initialize()"

Database location:

/root/xauusd_data_layer/data/xauusd.db
2. Data Flow
Biquote
   │
   ▼
Collector
   │
   ▼
SQLite
   │
   ▼
XAUUSD Data Layer API
   │
   ├── Internal consumers
   │
   └── External consumers

The main responsibility of this project is the data layer:

Market Data
    ↓
Collector
    ↓
SQLite
    ↓
HTTP API
    ↓
Consumers

Consumers should normally use the HTTP API instead of accessing the SQLite database directly.

3. Start the API
Internal access only

For consumers running on the same server:

cd /root/xauusd_data_layer

/root/xauusd_data_layer/.venv/bin/uvicorn \
    app.api.main:app \
    --host 127.0.0.1 \
    --port 8000

The API will be available locally at:

http://127.0.0.1:8000
4. Internal Consumer Usage

Internal consumers are applications running on the same VPS.

They can access the API through:

http://127.0.0.1:8000
Health
curl -s http://127.0.0.1:8000/health

Expected response:

{
  "status": "ok",
  "service": "xauusd-data-layer"
}
Current Price
curl -s http://127.0.0.1:8000/api/v1/price

Example:

{
  "symbol": "XAUUSD",
  "interval": "1m",
  "price": 4112.031,
  "time": 1791404820
}
Latest Candle
curl -s http://127.0.0.1:8000/api/v1/candles/latest

Example:

{
  "symbol": "XAUUSD",
  "interval": "1m",
  "candle": {
    "time": 1791404820,
    "open": 4111.67,
    "high": 4112.094,
    "low": 4111.296,
    "close": 4112.031,
    "tick_volume": 47,
    "spread": null,
    "real_volume": null
  }
}
Get Candles

Get the latest 100 candles:

curl -s 'http://127.0.0.1:8000/api/v1/candles?limit=100'

Get the latest 10 candles:

curl -s 'http://127.0.0.1:8000/api/v1/candles?limit=10'

Get the latest 1 candle:

curl -s 'http://127.0.0.1:8000/api/v1/candles?limit=1'

Maximum allowed limit:

1000
Get Candle by Timestamp

Example:

curl -s http://127.0.0.1:8000/api/v1/candles/1791404820

The timestamp is a Unix timestamp in seconds.

If the candle does not exist, the API returns HTTP 404.

Get Candles by Time Range

Example:

curl -s 'http://127.0.0.1:8000/api/v1/candles?start_time=1791404640&end_time=1791404820'

Both values are Unix timestamps in seconds.

5. External Consumer Usage

External consumers are applications running on another server or another network.

To allow external access, start the API on:

0.0.0.0

Run:

cd /root/xauusd_data_layer

/root/xauusd_data_layer/.venv/bin/uvicorn \
    app.api.main:app \
    --host 0.0.0.0 \
    --port 8000

The API will then listen on:

0.0.0.0:8000

Assume the server public IP is:

YOUR_SERVER_IP

The external API base URL is:

http://YOUR_SERVER_IP:8000
6. External Consumer Commands
Health

From another machine:

curl -s http://YOUR_SERVER_IP:8000/health
Current Price
curl -s http://YOUR_SERVER_IP:8000/api/v1/price
Latest Candle
curl -s http://YOUR_SERVER_IP:8000/api/v1/candles/latest
Latest 100 Candles
curl -s 'http://YOUR_SERVER_IP:8000/api/v1/candles?limit=100'
Latest 10 Candles
curl -s 'http://YOUR_SERVER_IP:8000/api/v1/candles?limit=10'
Candle by Timestamp
curl -s http://YOUR_SERVER_IP:8000/api/v1/candles/1791404820
Candles by Time Range
curl -s 'http://YOUR_SERVER_IP:8000/api/v1/candles?start_time=1791404640&end_time=1791404820'
7. Python Consumer

A Python application can consume the API using requests.

Install:

pip install requests

Example:

import requests

BASE_URL = "http://YOUR_SERVER_IP:8000"

response = requests.get(
    f"{BASE_URL}/api/v1/candles/latest",
    timeout=10,
)

response.raise_for_status()

data = response.json()

candle = data["candle"]

print("Symbol:", data["symbol"])
print("Interval:", data["interval"])
print("Time:", candle["time"])
print("Open:", candle["open"])
print("High:", candle["high"])
print("Low:", candle["low"])
print("Close:", candle["close"])
8. JavaScript Consumer

Example using fetch:

const BASE_URL = "http://YOUR_SERVER_IP:8000";

const response = await fetch(
    `${BASE_URL}/api/v1/candles/latest`
);

if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
}

const data = await response.json();

console.log(data);
console.log("Current price:", data.candle.close);
9. API Endpoints
Health
GET /health

Purpose:

Check whether the API process is responding.
Candles
GET /api/v1/candles

Query parameters:

limit
start_time
end_time

Example:

/api/v1/candles?limit=100
Latest Candle
GET /api/v1/candles/latest
Candle by Timestamp
GET /api/v1/candles/{timestamp}

Example:

/api/v1/candles/1791404820
Current Price
GET /api/v1/price

The current price is the close value of the latest stored candle.

10. API Documentation

When the API is running, interactive documentation is available.

Swagger UI:

http://127.0.0.1:8000/docs

ReDoc:

http://127.0.0.1:8000/redoc

OpenAPI schema:

http://127.0.0.1:8000/openapi.json

For external access:

http://YOUR_SERVER_IP:8000/docs
11. Database

The runtime database is:

/root/xauusd_data_layer/data/xauusd.db

SQLite table:

candles

Schema:

CREATE TABLE IF NOT EXISTS candles (
    time INTEGER PRIMARY KEY,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    tick_volume INTEGER,
    spread INTEGER,
    real_volume INTEGER
);
12. Direct SQLite Access

Direct SQLite access is intended for administration, diagnostics, and maintenance.

Consumers should normally use the HTTP API.

Open the database:

sqlite3 /root/xauusd_data_layer/data/xauusd.db

Check row count:

SELECT COUNT(*) FROM candles;

Get the latest candle:

SELECT *
FROM candles
ORDER BY time DESC
LIMIT 1;

Get the latest 10 candles:

SELECT *
FROM candles
ORDER BY time DESC
LIMIT 10;

Exit:

.quit
13. Collector

The collector receives XAUUSD market data from Biquote.

The main collector components are:

app/collector/biquote.py
app/collector/service.py
app/bootstrap/collector_runtime.py

Run the collector runtime:

cd /root/xauusd_data_layer

/root/xauusd_data_layer/.venv/bin/python \
    -m app.bootstrap.collector_runtime

The collector continuously polls for new closed candles.

Default polling interval:

5 seconds
14. Collector Architecture
Biquote API
     │
     ▼
BiquoteClient
     │
     ▼
CollectorService
     │
     ▼
SQLite

The collector is responsible for data acquisition.

The API is responsible for serving stored data.

These responsibilities are intentionally separated.

15. Database Layer

Database operations are implemented in:

app/database/database.py

Available operations include:

connect
initialize
get_candle
get_candles
get_latest_candle
get_candle_count
upsert_candle

The API uses these database functions instead of implementing SQL queries directly inside API routes.

16. Configuration

Project configuration is located in:

app/config.py

Important settings include:

SYMBOL = XAUUSD
INTERVAL = 1m
DATABASE_PATH = data/xauusd.db
BIQUOTE_BASE_URL = https://biquote.io/api
BIQUOTE_TIMEOUT = 10
COLLECTOR_POLL_SECONDS = 5
17. Project Structure
xauusd_data_layer/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   ├── archive/
│   │   └── __init__.py
│   │
│   ├── bootstrap/
│   │   ├── __init__.py
│   │   └── collector_runtime.py
│   │
│   ├── collector/
│   │   ├── __init__.py
│   │   ├── biquote.py
│   │   └── service.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── __init__.py
│   └── config.py
│
├── archive/
├── data/
│   └── xauusd.db
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
18. Internal vs External Consumers
Internal

Applications running on the same server should use:

http://127.0.0.1:8000

Example:

curl -s http://127.0.0.1:8000/api/v1/price
External

Applications running on another server should use:

http://YOUR_SERVER_IP:8000

Example:

curl -s http://YOUR_SERVER_IP:8000/api/v1/price

The API must be started with:

--host 0.0.0.0

for direct external access.

19. Recommended Consumer Rule

The preferred architecture is:

Consumer
   │
   ▼
HTTP API
   │
   ▼
Database Layer
   │
   ▼
SQLite

Do not duplicate database access logic in consumer applications.

Consumers should use the API endpoints.

For example:

Price:
GET /api/v1/price

Latest candle:
GET /api/v1/candles/latest

Historical candles:
GET /api/v1/candles?limit=100

Specific candle:
GET /api/v1/candles/{timestamp}
20. Security

The current API does not implement authentication.

Directly exposing:

0.0.0.0:8000

to the public Internet should therefore be considered a development/testing configuration.

For production deployment, the API should eventually be placed behind a proper network boundary such as:

Client
  ↓
HTTPS / Reverse Proxy
  ↓
Authentication / Access Control
  ↓
FastAPI
  ↓
SQLite

Potential production additions include:

HTTPS
Authentication
API keys
IP allowlists
Rate limiting
Reverse proxy
Firewall rules
systemd service

These are future deployment concerns and are not currently part of the read-only API implementation.

21. Backup

The SQLite database can be backed up with:

cp \
    /root/xauusd_data_layer/data/xauusd.db \
    /root/xauusd_data_layer/data/xauusd.db.backup

For a SQLite-safe backup while the database is active:

sqlite3 \
    /root/xauusd_data_layer/data/xauusd.db \
    ".backup '/root/xauusd_data_layer/data/xauusd_backup.db'"
22. Development Checks

Check Python version:

python3 --version

Check virtual environment Python:

/root/xauusd_data_layer/.venv/bin/python --version

Check API import:

cd /root/xauusd_data_layer

/root/xauusd_data_layer/.venv/bin/python \
    -c "from app.api.main import app; print('API IMPORT: PASS')"

Check database initialization:

cd /root/xauusd_data_layer

/root/xauusd_data_layer/.venv/bin/python \
    -c "from app.database import initialize; initialize(); print('DATABASE INIT: PASS')"
23. Git

Repository:

https://github.com/sina1991/db-gold

Remote:

git@github.com:sina1991/db-gold.git

Branch:

master

Check status:

cd /root/xauusd_data_layer
git status

Check remote:

git remote -v

Pull:

git pull origin master

Commit changes:

git add .
git commit -m "Update XAUUSD data layer"

Push:

git push origin master
24. Runtime Database and Git

The runtime SQLite database is intentionally excluded from Git.

The following pattern is ignored:

data/*.db

Therefore:

/root/xauusd_data_layer/data/xauusd.db

is runtime data and is not committed to the repository.

25. Project Independence

This project is independent from the legacy project:

/root/metatrader

The legacy application is not modified by this project.

The XAUUSD data layer has its own:

source code
virtual environment
database
API
collector
configuration
Git repository
26. Current Scope

The current project provides:

XAUUSD 1-minute market data
Biquote collector
SQLite storage
Read-only FastAPI
Current price endpoint
Latest candle endpoint
Historical candle endpoint
Time-range candle queries
Internal HTTP access
External HTTP access
Python consumer example
JavaScript consumer example
OpenAPI documentation
27. Future Scope

Possible future extensions include:

Authentication
HTTPS
API keys
Rate limiting
systemd service hardening
Reverse proxy
Historical data management
Automatic archive management
Additional market intervals
Additional symbols
Data validation
Monitoring
Metrics
Health checks with database validation

Future features should preserve the separation between:

Collector
Database
API
Consumers

and should not introduce duplicated business logic into API or consumer applications.
