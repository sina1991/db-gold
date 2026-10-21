"""Allowlisted modules available to dashboard slots.

This registry describes UI modules. It does not execute arbitrary code.
"""

MODULES = (
    {
        "id": "empty",
        "name": "Empty Slot",
        "description": "Leave this slot empty.",
    },
    {
        "id": "dashboard-health",
        "name": "Dashboard Health",
        "description": "Show the dashboard service health.",
    },
    {
        "id": "theme-summary",
        "name": "Theme Summary",
        "description": "Show the current theme configuration.",
    },
    {
        "id": "slot-note",
        "name": "Slot Note",
        "description": "A note saved locally in this browser for this slot.",
    },
)


def list_modules() -> list[dict[str, str]]:
    """Return JSON-safe copies of the registered module definitions."""
    return [dict(module) for module in MODULES]


def get_module(module_id: str) -> dict[str, str] | None:
    """Return one registered module, or None if it is not allowlisted."""
    for module in MODULES:
        if module["id"] == module_id:
            return dict(module)
    return None
