from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path


DEFAULT_EXTENSIONS = {".md", ".txt", ".json", ".py"}


def collect_desktop_entries(
    root: Path,
    limit: int = 5,
    *,
    include_extensions: set[str] | None = None,
    exclude_globs: list[str] | None = None,
) -> list[str]:
    include_extensions = include_extensions or DEFAULT_EXTENSIONS
    exclude_globs = exclude_globs or []

    entries: list[str] = []
    for path in sorted(root.rglob("*")):
        if len(entries) >= limit:
            break
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        rel_str = rel.as_posix()
        if any(part.startswith(".") for part in rel.parts):
            continue
        if any(fnmatch.fnmatch(rel_str, pattern) for pattern in exclude_globs):
            continue
        if path.suffix.lower() not in include_extensions:
            continue
        if path.name.endswith(".pyc") or "__pycache__" in path.parts:
            continue
        try:
            snippet = path.read_text(errors="ignore").strip()[:240]
        except OSError:
            continue
        entries.append(f"## {rel_str}\n{snippet}\n")
    return entries


def build_desktop_header(
    root: Path,
    limit: int = 5,
    *,
    include_extensions: set[str] | None = None,
    exclude_globs: list[str] | None = None,
) -> str:
    entries = collect_desktop_entries(
        root,
        limit=limit,
        include_extensions=include_extensions,
        exclude_globs=exclude_globs,
    )
    body = "\n".join(entries) if entries else "No local desktop files selected."
    return f"<DESKTOP>\n# Trusted Local Desktop\n\nRoot: {root}\n\n{body}\n</DESKTOP>"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--include-ext",
        action="append",
        default=[],
        help="Extension to include, for example --include-ext .md",
    )
    parser.add_argument(
        "--exclude-glob",
        action="append",
        default=[],
        help="Glob to exclude relative to the root, for example --exclude-glob 'tests/*'",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    include_extensions = set(args.include_ext) if args.include_ext else DEFAULT_EXTENSIONS
    print(
        build_desktop_header(
            root,
            limit=args.limit,
            include_extensions=include_extensions,
            exclude_globs=args.exclude_glob,
        )
    )


if __name__ == "__main__":
    main()
