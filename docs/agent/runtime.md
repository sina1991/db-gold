# Runtime and Operations

## systemd units

### API
- Unit: `xauusd-data-layer-api.service`
- Working directory: `/root/xauusd_data_layer`
- Entry point: `app.api.main:app`
- Server: Uvicorn on `0.0.0.0:8000`
- Restart policy: `always`, with a 5-second delay

### Collector
- Unit: `xauusd-data-layer-collector.service`
- Working directory: `/root/xauusd_data_layer`
- Entry point: `app.bootstrap.collector_runtime`
- Restart policy: `always`, with a 5-second delay

## Configuration
Defined in `app/config.py`:
- Symbol: `XAUUSD`
- Interval: `1m`
- SQLite file: `data/xauusd.db`
- Upstream base URL: `https://biquote.io/api`
- HTTP timeout: 10 seconds
- Collector polling interval: 5 seconds

## Operational checks
Check unit state:
`systemctl status xauusd-data-layer-api.service xauusd-data-layer-collector.service`

Check API health:
`curl --max-time 3 -sS http://127.0.0.1:8000/health`

Check listener:
`ss -ltnp '( sport = :8000 )'`

Inspect logs:
`journalctl -u xauusd-data-layer-api.service -n 100 --no-pager`
`journalctl -u xauusd-data-layer-collector.service -n 100 --no-pager`

## Security note
The observed API listener binds to all IPv4 interfaces. Whether it is reachable
externally depends on host/network firewall rules. Verify access controls before
exposing it to untrusted networks.

Service state, process IDs, record counts, and listener state are time-sensitive;
recheck them when troubleshooting rather than treating this document as live status.

## Installer warning
`install.sh` requires root and installs system packages on supported Ubuntu
systems. If the project directory already contains a Git repository, the
installer fetches the configured branch and runs `git reset --hard origin/master`.
This can discard local tracked changes. Review the script and preserve needed
changes before running it; do not use it as a routine documentation check.
