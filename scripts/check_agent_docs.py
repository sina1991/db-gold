#!/usr/bin/env python3
"""Check generated indexes against current Python and key project files."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "docs/agent/code-index.json"
MANIFEST = ROOT / "docs/agent/source-manifest.json"
EXCLUDED = {".git", ".venv", "venv", "__pycache__"}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def python_files():
    result = []
    for folder in ("app", "scripts"):
        base = ROOT / folder
        if base.exists():
            result.extend(
                p for p in base.rglob("*.py")
                if not any(part in EXCLUDED for part in p.parts)
            )
    return sorted(set(result))

def manifest_files():
    paths = []
    for name in (
        "AGENTS.md", "README.md", ".gitignore",
        "requirements.txt", "install.sh",
    ):
        p = ROOT / name
        if p.is_file():
            paths.append(p)
    for pattern in (
        "systemd/*.service", "docs/agent/*.md",
        ".githooks/*", ".github/workflows/*",
    ):
        paths.extend(ROOT.glob(pattern))
    paths.extend(python_files())
    return sorted(set(p for p in paths if p.is_file()))

def compare(label, expected, actual):
    added = sorted(actual.keys() - expected.keys())
    deleted = sorted(expected.keys() - actual.keys())
    changed = sorted(
        p for p in actual.keys() & expected.keys()
        if actual[p] != expected[p]
    )
    for kind, paths in (("New", added), ("Missing", deleted), ("Changed", changed)):
        for path in paths:
            print(f"{label} {kind}: {path}")
    return not (added or deleted or changed)

def main():
    for p in (INDEX, MANIFEST):
        if not p.is_file():
            print(f"STALE: generated file missing: {p.relative_to(ROOT)}")
            print("Regenerate: .venv/bin/python scripts/generate_agent_docs.py")
            return 1

    index_data = json.loads(INDEX.read_text(encoding="utf-8"))
    indexed_python = {
        f["path"]: f["sha256"] for f in index_data.get("files", [])
    }
    current_python = {
        p.relative_to(ROOT).as_posix(): sha256(p) for p in python_files()
    }
    ok_python = compare("Python index", indexed_python, current_python)

    manifest_data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    indexed_files = {
        f["path"]: f["sha256"] for f in manifest_data.get("files", [])
    }
    current_files = {
        p.relative_to(ROOT).as_posix(): sha256(p) for p in manifest_files()
    }
    ok_manifest = compare("Source manifest", indexed_files, current_files)

    if not (ok_python and ok_manifest):
        print("STALE: regenerate indexes and review handbook prose.")
        print("Run: .venv/bin/python scripts/generate_agent_docs.py")
        return 1

    print(f"OK: Python index matches {len(current_python)} files.")
    print(f"OK: source manifest matches {len(current_files)} files.")
    print("Note: matching hashes do not prove prose documentation is accurate.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
