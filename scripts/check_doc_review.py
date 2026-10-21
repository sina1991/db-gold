#!/usr/bin/env python3
"""Report handbook documents that should be reviewed after source changes."""
import argparse
import subprocess
import sys

RULES = {
    "docs/agent/architecture.md": (
        "app/collector/",
        "app/bootstrap/",
        "app/database/",
        "app/config.py",
    ),
    "docs/agent/contracts.md": (
        "app/api/",
        "app/database/",
        "app/config.py",
    ),
    "docs/agent/runtime.md": (
        "systemd/",
        "install.sh",
        "app/bootstrap/",
        "app/config.py",
        "requirements.txt",
    ),
}


def changed_files(base=None):
    if base:
        command = ["git", "diff", "--name-only", f"{base}...HEAD"]
    else:
        command = ["git", "diff", "--cached", "--name-only"]

    result = subprocess.run(
        command, text=True, capture_output=True, check=False
    )
    if result.returncode:
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(result.returncode)

    return sorted(set(result.stdout.splitlines()))


def matches(path, patterns):
    return any(
        path == pattern or path.startswith(pattern)
        for pattern in patterns
    )


def main():
    parser = argparse.ArgumentParser(
        description="Report handbook documents that may need review."
    )
    parser.add_argument(
        "--base",
        help="Git base revision for comparison; defaults to staged changes.",
    )
    args = parser.parse_args()

    files = changed_files(args.base)
    if not files:
        print("No changed files to review.")
        return 0

    print("Changed files:")
    for path in files:
        print(f"  {path}")

    source_changes = [
        path for path in files
        if path.startswith(("app/", "systemd/"))
        or path in ("install.sh", "requirements.txt")
    ]

    print("\nDocumentation review:")
    warnings = 0
    for doc, patterns in RULES.items():
        relevant = [
            path for path in source_changes if matches(path, patterns)
        ]
        if relevant:
            warnings += 1
            print(f"REVIEW REQUIRED: {doc}")
            for path in relevant:
                print(f"  triggered by: {path}")

    if warnings:
        print(
            "\nThese are review prompts, not proof that the documentation "
            "is incorrect. Read the relevant source and update prose if needed."
        )
    else:
        print("No architecture/contracts/runtime review rule was triggered.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
