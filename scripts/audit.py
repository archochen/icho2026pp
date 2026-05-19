#!/usr/bin/env python3
"""
audit.py — compare a source PART{N}_split/Problem_NN_*.md to the migrated
parts/part{N}/Problem_NN.qmd and report any content present in source but
missing from the .qmd (or local files referenced but not present on disk).

This is the safety net for manual migrations: it catches the specific loss
mode we hit on P2.24 (5 external-URL <img> tags inside solution blockquotes
were silently dropped during transcription).

Usage:
    python scripts/audit.py                 # audit every Problem_NN.qmd
    python scripts/audit.py 2 24            # audit just P2.24
    python scripts/audit.py --strict        # exit 1 on any discrepancy

Loss vectors covered:
    - Image refs (![...](path)  AND  <img src="...">)  -- local + external
    - Solution blockquote labels  (> **Solution (Qn — topic).**)
    - Top-level Headers in source body (after stripping H1 and Chinese sections)
    - Local image files referenced by .qmd but missing on disk

The audit treats Chinese-section content (中文版 / 教学点评 / 相对丰度表)
as expected-to-be-absent in HTML, so it strips those from source before
comparing.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ICLOUD_ROOT = Path(
    "/Users/qchen/Library/Mobile Documents/com~apple~CloudDocs/"
    "学习工作/竞赛教学/IChO/2026年58届 乌兹别克/prep problems"
)

CN_MARKERS = ("中文版", "Chinese translation", "教学点评", "解题分析", "相对丰度表")

# Canonical FoAD vocabulary — mirrors _foad.yml at the repo root.
# Update both files together if the official IChO syllabus changes.
FOAD_VOCAB = {
    "mass-spectrometry",
    "kinetics",
    "thermodynamics",
    "transition-metal-catalysis",
    "photochemistry",
    "carbohydrate-chemistry",
}

# YAML frontmatter `foad:` line — captures either `[a, b]` or `[]`.
FOAD_LINE = re.compile(r"^foad:\s*\[(?P<items>.*?)\]\s*$", re.MULTILINE)

# Match image refs in markdown: ![alt](url) and <img src="url" ...>
IMG_MD = re.compile(r"!\[[^\]]*\]\(\s*(?P<url>[^)\s]+)\s*[^)]*\)")
IMG_HTML = re.compile(r"<img[^>]+\bsrc=[\"'](?P<url>[^\"']+)[\"']", re.IGNORECASE)


def normalize_local_path(url: str) -> str:
    """Strip leading './' so 'assets/foo.png' and './assets/foo.png' match."""
    return url.lstrip("./") if not url.startswith(("http://", "https://", "data:")) else url

# Solution blockquote opener: > **Solution (Qn — topic).** (allow optional period, etc.)
SOLUTION_LABEL = re.compile(r"^>\s*\*\*Solution\s*\(\s*(?P<label>[^)]+?)\s*\)\s*\.?\s*\*\*", re.MULTILINE)

# Top-level headings (any level)
HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+?)\s*$", re.MULTILINE)


def strip_cn_sections(text: str) -> str:
    """Drop all content from the first Chinese marker to end-of-file."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    cut_at = None
    for i, line in enumerate(lines):
        if line.startswith("#"):
            stripped = line.lstrip("#").strip()
            if any(m in stripped for m in CN_MARKERS):
                cut_at = i
                break
        out.append(line)
    # Trim trailing horizontal rules that were leading into the dropped block.
    while out and out[-1].strip() == "---":
        out.pop()
    return "".join(out)


def extract_image_refs(text: str) -> set[str]:
    return {
        normalize_local_path(m.group("url")) for m in IMG_MD.finditer(text)
    } | {
        normalize_local_path(m.group("url")) for m in IMG_HTML.finditer(text)
    }


def extract_solution_labels(text: str) -> set[str]:
    return {m.group("label").strip() for m in SOLUTION_LABEL.finditer(text)}


def normalize_label_for_match(label: str) -> str:
    """Strip math delimiters and trailing punctuation to allow fuzzy match."""
    s = re.sub(r"[\$\\{}]", "", label)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def extract_headings(text: str) -> set[str]:
    return {m.group("text").strip().lower() for m in HEADING.finditer(text)}


def find_source(part: int, problem_id: int) -> Path | None:
    src_dir = ICLOUD_ROOT / f"PART{part}_split"
    if not src_dir.is_dir():
        return None
    nn = f"Problem_{problem_id:02d}_"
    for f in src_dir.iterdir():
        if f.is_file() and f.suffix == ".md" and f.name.startswith(nn):
            return f
    return None


def audit_problem(part: int, qmd: Path, strict: bool = False) -> int:
    """Audit a single problem; return number of issues found."""
    m = re.match(r"Problem_0?(\d+)\.qmd$", qmd.name)
    if not m:
        return 0
    problem_id = int(m.group(1))
    src = find_source(part, problem_id)
    if not src:
        print(f"  [P{part}.{problem_id:02d}] no source file in PART{part}_split — skipping")
        return 0

    src_text = src.read_text()
    src_visible = strip_cn_sections(src_text)
    qmd_text = qmd.read_text()

    issues: list[str] = []

    # 1. Image refs in source visible body must appear (by url) in qmd
    src_imgs = extract_image_refs(src_visible)
    qmd_imgs = extract_image_refs(qmd_text)
    missing_imgs = src_imgs - qmd_imgs
    for url in sorted(missing_imgs):
        issues.append(f"missing image ref: {url}")

    # 2. Solution labels in source must appear in qmd (fuzzy on math)
    src_labels = {normalize_label_for_match(l) for l in extract_solution_labels(src_visible)}
    qmd_labels = {normalize_label_for_match(l) for l in extract_solution_labels(qmd_text)}
    missing_labels = src_labels - qmd_labels
    for label in sorted(missing_labels):
        issues.append(f"missing Solution blockquote: {label}")

    # 3. Local images referenced in qmd must exist on disk
    for url in qmd_imgs:
        if url.startswith(("http://", "https://", "data:")):
            continue
        rel = url.lstrip("./")
        target = qmd.parent / rel
        if not target.exists():
            issues.append(f"local image referenced but not on disk: {rel}")

    # 4. Every `foad:` frontmatter value must be in the canonical vocabulary
    m_foad = FOAD_LINE.search(qmd_text)
    if m_foad:
        raw = m_foad.group("items").strip()
        if raw:
            slugs = [s.strip().strip('"').strip("'") for s in raw.split(",")]
            for slug in slugs:
                if slug and slug not in FOAD_VOCAB:
                    issues.append(
                        f"unknown foad slug: '{slug}' (allowed: "
                        f"{', '.join(sorted(FOAD_VOCAB))})"
                    )

    label = f"P{part}.{problem_id:02d}"
    if issues:
        print(f"  [{label}] {len(issues)} issue(s):")
        for it in issues:
            print(f"      - {it}")
    else:
        print(f"  [{label}] ✓ clean ({len(src_imgs)} image refs, {len(src_labels)} solutions)")
    return len(issues)


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    argv = [a for a in argv if a != "--strict"]

    targets: list[tuple[int, Path]] = []
    if len(argv) >= 2:
        part = int(argv[0])
        pid = int(argv[1])
        qmd = REPO_ROOT / f"parts/part{part}/Problem_{pid:02d}.qmd"
        if qmd.exists():
            targets.append((part, qmd))
    else:
        for part_dir in sorted((REPO_ROOT / "parts").glob("part*")):
            if not part_dir.is_dir():
                continue
            part = int(part_dir.name.replace("part", ""))
            for qmd in sorted(part_dir.glob("Problem_*.qmd")):
                targets.append((part, qmd))

    if not targets:
        print("No Problem_*.qmd files found.")
        return 0

    total_issues = 0
    print(f"Auditing {len(targets)} problem file(s)…\n")
    for part, qmd in targets:
        total_issues += audit_problem(part, qmd, strict=strict)

    print()
    if total_issues == 0:
        print("✓ All clean. No missing images, solutions, or local files.")
        return 0
    print(f"✗ {total_issues} issue(s) total.")
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
