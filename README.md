# XAUUSD Data Layer

Independent XAUUSD 1-minute data layer.

Responsibilities:

- Receive XAUUSD 1-minute candles from Biquote.
- Store current and historical data in SQLite.
- Optionally perform one-time historical bootstrap through SSH.
- Verify overlap between old historical data and new Biquote data.
- Continue collecting new candles.
- Archive completed Forex weeks as ISO Week SQLite files.

The historical source is the old server database.
The old application is not modified by this project.
