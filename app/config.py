from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
ARCHIVE_DIR = PROJECT_ROOT / "archive"
DATABASE_PATH = DATA_DIR / "xauusd.db"

SYMBOL = "XAUUSD"
INTERVAL = "1m"

BIQUOTE_BASE_URL = "https://biquote.io/api"
BIQUOTE_TIMEOUT = 10
COLLECTOR_POLL_SECONDS = 5

CANDLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS candles (
    time INTEGER PRIMARY KEY,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    tick_volume INTEGER,
    spread INTEGER,
    real_volume INTEGER
)
"""
