# Agent Guide

Read this file first, then consult the relevant files as needed:
- `docs/agent/architecture.md`: system design and data flow.
- `docs/agent/contracts.md`: API and data contracts.
- `docs/agent/runtime.md`: deployment and operations.
- `docs/agent/code-index.json`: Python symbol navigation.

## Rules
- Treat source code as the authority; generated indexes are navigation aids.
- Locate relevant symbols in `docs/agent/code-index.json` before opening source.
- Inspect only the relevant function/class and its direct dependencies.
- Do not modify runtime code or database schema without checking callers,
  API contracts, and persistence behavior.
- Never expose secrets or copy credentials into documentation.
- After code changes, run the relevant tests/checks and regenerate the index.
- Update architecture/contracts docs whenever behavior or interfaces change.
- Runtime status is a time-sensitive snapshot, not permanent project truth.

## Project
- Python application; FastAPI API; SQLite persistence.
- Market: XAUUSD, interval: 1m.
- Collector source: Biquote HTTP API.
- Database path: `data/xauusd.db`.
- API entry point: `app.api.main:app`.
- Collector entry point: `app.bootstrap.collector_runtime`.
- Systemd units: `systemd/`.

## Documentation generator
Run:
`/root/xauusd_data_layer/.venv/bin/python scripts/generate_agent_docs.py`

## Required workflow after code changes
1. Run the relevant project tests, if available.
2. Regenerate the source index:
   `.venv/bin/python scripts/generate_agent_docs.py`
3. Check that the index is current:
   `.venv/bin/python scripts/check_agent_docs.py`
4. Review `docs/agent/code-index.json` and update architecture/contracts/runtime
   documentation if behavior, persistence, API, configuration, or deployment changed.
5. Review `git diff` and `git status --short` before committing.
6. Never assume the documentation is correct just because the index is fresh:
   the index detects source changes; it does not validate prose documentation.

- `scripts/check_agent_docs.py` checks both the Python index and
  `docs/agent/source-manifest.json`, which hashes key project, deployment,
  and handbook files.
- After changing README, requirements, installer, systemd units, or handbook
  Markdown, regenerate the manifest and inspect the relevant documentation.
