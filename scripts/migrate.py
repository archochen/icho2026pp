#!/usr/bin/env python3
"""
migrate.py — convert a PART{N}_split/Problem_NN_*.md source file into a
parts/part{N}/Problem_NN.qmd file, deterministically and without any
manual transcription.

Why this exists: the only way an image, blockquote, or equation can be
silently lost during migration is if a human types out the body by hand.
This script reads the source bytes, applies a small set of regex
transforms, prepends frontmatter, and writes the result. No content is
ever dropped.

Usage:
    python scripts/migrate.py 2 23          # migrate P2.23 from PART2_split/
    python scripts/migrate.py 2 23 --force  # overwrite an existing qmd
    python scripts/migrate.py 2 --all       # migrate every Part-2 source

After migrating, run `python scripts/audit.py` to verify nothing was lost.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ICLOUD_ROOT = Path(
    "/Users/qchen/Library/Mobile Documents/com~apple~CloudDocs/"
    "学习工作/竞赛教学/IChO/2026年58届 乌兹别克/prep problems"
)
DISCORD_URL = "https://discord.gg/CHANGE-ME"

H1_PROBLEM = re.compile(r"^\s*# Problem \d+\.\s*(?P<title>.+?)\s*$", re.MULTILINE)
H1_PART_BOLD = re.compile(r"^\s*#\s+\*\*Part\s+(\d+)\.\s*(.+?)\*\*\s*$", re.MULTILINE)
H1_CN_PART = re.compile(r"^\s*#\s+(第[一二三四五六七八九十]+部分.*)$", re.MULTILINE)
H1_CN_TITLE = re.compile(r"^\s*#\s+(第\s*\d+\s*题.*)$", re.MULTILINE)
H1_CN_TABLE = re.compile(r"^\s*#\s+(相对丰度表.*)$", re.MULTILINE)
DIFFICULTY = re.compile(r"难度评级[：:]\s*([★☆]+)")
# Maintainer-internal Codex revision notes from the source archive; strip them
# (along with their trailing empty blockquote line) so they never reach the
# rendered site.
CODEX_NOTE = re.compile(
    r"^> \*\*Revision note:\*\* Revised by Codex on [^\n]*\n(?:>\s*\n)?",
    re.MULTILINE,
)

LOCAL_IMG_MD = re.compile(r"!\[[^\]]*\]\(\s*((?:\./)?(?:images|assets)/[^)\s]+)\s*\)")
LOCAL_IMG_HTML = re.compile(r'<img[^>]+\bsrc=["\']((?:\./)?(?:images|assets)/[^"\']+)["\']')


def parse_filename(name: str) -> tuple[int, str]:
    """Extract (problem_id, status_hint) from a source filename stem.

    Examples:
      Problem_23_HAT_and_XAT_HalAT - with Key and Analysis - TBC.md  -> (23, 'tbc')
      Problem_01_Khoja_Nasreddin_is_now_a_chemist - with Key and Analysis.md -> (1, 'final')
      Problem_05_Haber-Bosch_process.md -> (5, 'not-started')
    """
    stem = Path(name).stem
    m = re.match(r"Problem_0?(\d+)_", stem)
    if not m:
        raise ValueError(f"unrecognised filename: {name}")
    pid = int(m.group(1))
    if "TBC" in stem:
        status = "tbc"
    elif "draft" in stem.lower():
        status = "draft"
    elif "with Key" in stem or "with Analysis" in stem:
        status = "final"  # maintainer may downgrade to revised/draft as needed
    else:
        status = "not-started"
    return pid, status


def extract_title(body: str) -> str:
    m = H1_PROBLEM.search(body)
    return m.group("title").strip() if m else "(untitled)"


def extract_difficulty(body: str) -> int:
    """Count black stars in '难度评级：★★★★☆' line; default 3 if not found."""
    m = DIFFICULTY.search(body)
    if not m:
        return 3
    return m.group(1).count("★")


def transform(body: str) -> str:
    body = H1_PROBLEM.sub("", body, count=1).lstrip("\n")
    body = H1_PART_BOLD.sub(r"## Part \1 — \2", body)
    body = H1_CN_PART.sub(r"## \1", body)
    body = H1_CN_TITLE.sub(r"## \1", body)
    body = H1_CN_TABLE.sub(r"## \1", body)
    body = CODEX_NOTE.sub("", body)
    return body


def build_frontmatter(part: int, pid: int, title: str, status: str, difficulty: int) -> str:
    today = _dt.date.today().isoformat()
    return (
        "---\n"
        f'title: "P{part}.{pid:02d} — {title}"\n'
        f"problem-id: {pid}\n"
        f"status: {status}\n"
        f"difficulty: {difficulty}\n"
        "foad: []\n"
        "topics: []\n"
        f'date: "{today}"\n'
        'description: ""\n'
        "---\n\n"
        '::: {.callout-note appearance="simple" icon=false}\n'
        f"**Found an issue?** Post the problem number (**P{part}.{pid:02d}**) and the **step** on Discord.\n"
        f"[💬 Discuss on Discord →]({DISCORD_URL}){{.discord-cta}}\n"
        ":::\n\n"
    )


def referenced_local_images(body: str) -> set[str]:
    refs: set[str] = set()
    for m in LOCAL_IMG_MD.finditer(body):
        refs.add(m.group(1).lstrip("./"))
    for m in LOCAL_IMG_HTML.finditer(body):
        refs.add(m.group(1).lstrip("./"))
    return refs


def copy_images(src_dir: Path, dst_dir: Path, refs: set[str]) -> tuple[int, list[str]]:
    copied = 0
    missing: list[str] = []
    for ref in sorted(refs):
        src = src_dir / ref
        dst = dst_dir / ref
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            missing.append(ref)
            continue
        if dst.exists() and dst.stat().st_size == src.stat().st_size:
            copied += 1
            continue
        shutil.copy2(src, dst)
        copied += 1
    return copied, missing


def find_source(part: int, pid: int) -> Path | None:
    src_dir = ICLOUD_ROOT / f"PART{part}_split"
    if not src_dir.is_dir():
        return None
    prefix = f"Problem_{pid:02d}_"
    for f in src_dir.iterdir():
        if f.is_file() and f.suffix == ".md" and f.name.startswith(prefix):
            return f
    return None


def migrate(part: int, pid: int, *, force: bool = False) -> int:
    src = find_source(part, pid)
    if not src:
        print(f"  [P{part}.{pid:02d}] no source file in PART{part}_split — skipping")
        return 1

    dst = REPO_ROOT / f"parts/part{part}/Problem_{pid:02d}.qmd"
    if dst.exists() and not force:
        print(f"  [P{part}.{pid:02d}] {dst.relative_to(REPO_ROOT)} exists — pass --force to overwrite")
        return 1

    raw = src.read_text()
    title = extract_title(raw)
    _, status_hint = parse_filename(src.name)
    difficulty = extract_difficulty(raw)
    body = transform(raw)

    fm = build_frontmatter(part, pid, title, status_hint, difficulty)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(fm + body)

    refs = referenced_local_images(body)
    copied, missing = copy_images(src.parent, dst.parent, refs)

    rel = dst.relative_to(REPO_ROOT)
    print(
        f"  [P{part}.{pid:02d}] wrote {rel} "
        f"(status={status_hint}, difficulty={difficulty}, "
        f"{copied}/{len(refs)} local images)"
    )
    if missing:
        print(f"    WARNING: {len(missing)} referenced image(s) not found in source:")
        for m in missing:
            print(f"      - {m}")
    return 0


def all_problems_in_part(part: int) -> list[int]:
    src_dir = ICLOUD_ROOT / f"PART{part}_split"
    if not src_dir.is_dir():
        return []
    ids: set[int] = set()
    for f in src_dir.iterdir():
        m = re.match(r"Problem_0?(\d+)_", f.name)
        if m and f.suffix == ".md":
            ids.add(int(m.group(1)))
    return sorted(ids)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("part", type=int, help="Part number (1, 2, or 3)")
    p.add_argument("problem", nargs="?", type=int, help="Problem number; omit with --all")
    p.add_argument("--all", action="store_true", help="Migrate every source in this part")
    p.add_argument("--force", action="store_true", help="Overwrite an existing qmd")
    args = p.parse_args(argv)

    if args.all:
        ids = all_problems_in_part(args.part)
        if not ids:
            print(f"No sources found in PART{args.part}_split/")
            return 1
        print(f"Migrating {len(ids)} problem(s) from PART{args.part}_split…\n")
        rc = 0
        for pid in ids:
            rc |= migrate(args.part, pid, force=args.force)
        return rc

    if args.problem is None:
        p.error("provide a problem number, or use --all")

    return migrate(args.part, args.problem, force=args.force)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
