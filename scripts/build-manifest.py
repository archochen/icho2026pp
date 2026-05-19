#!/usr/bin/env python3
"""
build-manifest.py — write _site/manifest.json with per-problem frontmatter.

Quarto's auto-generated `_site/listings.json` only contains URL strings for
each listing item, not the full frontmatter metadata. The Syllabus page
needs each problem's `foad:` list to populate the per-FoAD "On this site"
cross-links, so we generate a small companion manifest here.

Schema (a JSON array of problem entries):

    [
      {
        "title": "P2.21 — Catalyst C",
        "problem-id": 21,
        "status": "tbc",
        "difficulty": 3,
        "foad": ["mass-spectrometry", "transition-metal-catalysis"],
        "topics": ["wilkinson-catalyst", "hydrogenation", ...],
        "date": "2026-05-18",
        "path": "parts/part2/Problem_21.html"
      },
      ...
    ]

Run AFTER `quarto render`. Idempotent and fast (just scans .qmd files).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "parts"
OUT = ROOT / "_site" / "manifest.json"

FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
LIST_FIELD = re.compile(r"^(?P<key>[a-z_-]+):\s*\[(?P<items>.*?)\]\s*$", re.MULTILINE)
SCALAR_FIELD = re.compile(r"^(?P<key>[a-z_-]+):\s*(?P<val>.+?)\s*$", re.MULTILINE)

WANTED_FIELDS = (
    "title", "problem-id", "status", "difficulty",
    "foad", "topics", "date", "description",
)


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def _parse_list(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return []
    # Naive comma split — frontmatter list items are simple slugs/strings;
    # nested brackets aren't used.
    return [_strip_quotes(x) for x in raw.split(",") if x.strip()]


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER.match(text)
    if not m:
        return {}
    block = m.group(1)
    out: dict = {}
    # Capture list-valued fields first (they have a specific `[...]` shape)
    list_keys: set[str] = set()
    for m in LIST_FIELD.finditer(block):
        out[m.group("key")] = _parse_list(m.group("items"))
        list_keys.add(m.group("key"))
    # Then scalar fields, skipping anything we already captured as a list
    for m in SCALAR_FIELD.finditer(block):
        key = m.group("key")
        if key in list_keys:
            continue
        raw = _strip_quotes(m.group("val"))
        if raw.isdigit():
            out[key] = int(raw)
        else:
            out[key] = raw
    return out


def derive_path(qmd: Path) -> str:
    """parts/part2/Problem_01.qmd -> parts/part2/Problem_01.html"""
    return str(qmd.relative_to(ROOT)).replace(".qmd", ".html")


def main() -> int:
    if not PARTS.is_dir():
        print(f"No parts/ directory at {PARTS}", file=sys.stderr)
        return 1

    items: list[dict] = []
    for qmd in sorted(PARTS.glob("**/Problem_*.qmd")):
        fm = parse_frontmatter(qmd.read_text())
        entry: dict = {"path": derive_path(qmd)}
        for k in WANTED_FIELDS:
            if k in fm:
                entry[k] = fm[k]
        items.append(entry)

    if not OUT.parent.exists():
        print(f"_site/ does not exist yet — run `quarto render` first", file=sys.stderr)
        return 1

    OUT.write_text(json.dumps(items, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(items)} problem(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
