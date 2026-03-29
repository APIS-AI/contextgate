from __future__ import annotations

import argparse
from pathlib import Path


def collect_desktop_entries(root: Path, limit: int = 5) -> list[str]:
    entries: list[str] = []
    for path in sorted(root.rglob("*")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        if len(entries) >= limit:
            break
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt", ".json", ".py"}:
            continue
        if path.name.endswith((".pyc",)) or "__pycache__" in path.parts:
            continue
            continue
        try:
            snippet = path.read_text(errors="ignore").strip()[:240]
        except OSError:
            continue
        rel = path.relative_to(root)
        entries.append(f"## {rel}\n{snippet}\n")
    return entries


def build_desktop_header(root: Path, limit: int = 5) -> str:
    entries = collect_desktop_entries(root, limit=limit)
    body = "\n".join(entries) if entries else "No local desktop files selected."
    return f"<DESKTOP>\n# Trusted Local Desktop\n\nRoot: {root}\n\n{body}\n</DESKTOP>"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    print(build_desktop_header(root, limit=args.limit))


if __name__ == "__main__":
    main()
