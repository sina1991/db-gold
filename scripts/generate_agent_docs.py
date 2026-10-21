#!/usr/bin/env python3
"""Generate Python symbol index and hashes for key project files."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs/agent/code-index.json"
MANIFEST = ROOT / "docs/agent/source-manifest.json"
EXCLUDED = {".git", ".venv", "venv", "__pycache__"}

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def source_files():
    paths = []
    for folder in ("app", "scripts"):
        base = ROOT / folder
        if base.exists():
            paths.extend(
                p for p in base.rglob("*.py")
                if not any(part in EXCLUDED for part in p.parts)
            )
    return sorted(set(paths))

def manifest_files():
    paths = []
    fixed = (
        "AGENTS.md", "README.md", ".gitignore",
        "requirements.txt", "install.sh",
    )
    for name in fixed:
        p = ROOT / name
        if p.is_file():
            paths.append(p)

    for pattern in (
        "systemd/*.service", "docs/agent/*.md",
        ".githooks/*", ".github/workflows/*",
    ):
        paths.extend(ROOT.glob(pattern))

    # Track code/tool changes as well as deployment and documentation changes.
    paths.extend(source_files())
    return sorted(set(p for p in paths if p.is_file()))


def write_output(path, content, check):
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            print(f"STALE: {path.relative_to(ROOT)}")
            return False
        print(f"OK: {path.relative_to(ROOT)} is up to date.")
        return True

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True

def imports_for(tree):
    result = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            result.append("." * node.level + (node.module or ""))
    return sorted(set(result))

def calls_for(node):
    calls = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        fn = child.func
        if isinstance(fn, ast.Name):
            calls.add(fn.id)
        elif isinstance(fn, ast.Attribute):
            parts = [fn.attr]
            base = fn.value
            while isinstance(base, ast.Attribute):
                parts.append(base.attr)
                base = base.value
            if isinstance(base, ast.Name):
                parts.append(base.id)
            calls.add(".".join(reversed(parts)))
    return sorted(calls)

def describe_node(node, parent=None):
    if isinstance(node, ast.ClassDef):
        kind, signature = "class", None
    elif isinstance(node, ast.AsyncFunctionDef):
        kind = "async_method" if parent else "async_function"
        signature = f"{node.name}({ast.unparse(node.args)})"
    elif isinstance(node, ast.FunctionDef):
        kind = "method" if parent else "function"
        signature = f"{node.name}({ast.unparse(node.args)})"
    else:
        return None

    doc = ast.get_docstring(node)
    item = {
        "name": node.name,
        "kind": kind,
        "line_start": node.lineno,
        "line_end": getattr(node, "end_lineno", node.lineno),
        "signature": signature,
        "returns": ast.unparse(node.returns)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.returns else None,
        "doc": doc.splitlines()[0][:240] if doc else None,
    }
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        item["calls"] = calls_for(node)
    if isinstance(node, ast.ClassDef):
        item["methods"] = [
            method_item
            for child in node.body
            if (method_item := describe_node(child, node.name)) is not None
        ]
    return item

def main():
    parser = argparse.ArgumentParser(
        description="Generate or check the Agent documentation indexes."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check generated files without modifying them.",
    )
    args = parser.parse_args()

    indexed = []
    errors = 0
    for path in source_files():
        raw = path.read_bytes()
        rel = path.relative_to(ROOT).as_posix()
        try:
            tree = ast.parse(raw, filename=rel)
            symbols = [
                item for node in tree.body
                if (item := describe_node(node)) is not None
            ]
            imports = imports_for(tree)
            parse_error = None
        except SyntaxError as exc:
            symbols, imports = [], []
            parse_error = f"{exc.msg} at line {exc.lineno}"
            errors += 1

        indexed.append({
            "path": rel,
            "sha256": sha256(raw),
            "bytes": len(raw),
            "parse_error": parse_error,
            "imports": imports,
            "symbols": symbols,
        })

    index_text = json.dumps({
        "format_version": 1,
        "purpose": "Python source navigation index; source code remains authoritative.",
        "files": indexed,
    }, indent=2, ensure_ascii=False) + "\n"
    index_ok = write_output(OUTPUT, index_text, args.check)

    manifest = []
    for path in manifest_files():
        raw = path.read_bytes()
        manifest.append({
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(raw),
            "bytes": len(raw),
        })
    manifest_text = json.dumps({
        "format_version": 1,
        "purpose": "Hashes of key source, deployment, and handbook files.",
        "files": manifest,
    }, indent=2, ensure_ascii=False) + "\n"
    manifest_ok = write_output(MANIFEST, manifest_text, args.check)

    symbols = sum(
        len(f["symbols"]) + sum(len(s.get("methods", [])) for s in f["symbols"])
        for f in indexed
    )
    print(f"Indexed Python files: {len(indexed)}")
    print(f"Symbols including class methods: {symbols}")
    print(f"Source/handbook manifest files: {len(manifest)}")
    print(f"Parse errors: {errors}")
    print(f"Outputs: {OUTPUT.relative_to(ROOT)}, {MANIFEST.relative_to(ROOT)}")
    if errors:
        raise SystemExit(1)
    if args.check and not (index_ok and manifest_ok):
        print("STALE: regenerate indexes and review handbook prose.")
        print("Run: .venv/bin/python scripts/generate_agent_docs.py")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
