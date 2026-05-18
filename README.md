# IChO 2026 Preparatory Problems — Solutions

Working solutions and pedagogical analyses for the **58th IChO (Uzbekistan, 2026)** preparatory problems. Markdown is the single source of truth; Quarto builds the website + (optional) per-problem PDFs.

## Stack

- **Quarto** ≥ 1.4 — site builder, supports KaTeX + mhchem out of the box.
- **GitHub Pages** — free hosting.
- **GitHub Actions** — auto-render and deploy on every push to `main`.
- **Discord** — student feedback channel; one server-wide invite linked from every page footer.

## Local workflow

```bash
# One-time
cd ~/code/icho2026-solutions

# Live preview while drafting (auto-reloads on save)
quarto preview

# One-shot render to ./_site
quarto render
```

## Editing a solution

Every problem lives at `parts/partN/Problem_NN.qmd`. Frontmatter:

```yaml
---
title: "P2.07 — Some title"
problem-id: 7
status: draft        # not-started | draft | revised | final | tbc
difficulty: 4        # 0–5, rendered as stars
topics: [organic, kinetics, isotopes]
date: "2026-05-18"
description: "One-sentence hook for the dashboard tooltip."
---
```

The status field drives:
- A colored badge at the top of the problem page (injected by `_extensions/status-badge/`).
- The Status column in the index dashboard (decorated by an inline script in `index.qmd`).

## Status lifecycle

| Status        | Meaning                                                                       |
| ------------- | ----------------------------------------------------------------------------- |
| `not-started` | No solution drafted yet.                                                      |
| `draft`       | First pass complete, internally cross-checked, **not** peer-reviewed.         |
| `revised`     | Incorporates at least one round of student or external feedback.              |
| `final`       | Answer key and pedagogical analysis stabilized; no expected changes.          |
| `tbc`         | A specific step is contested and waiting for verification. Flag it inline.    |

## Migrating an existing solution from `PART2_split/`

Use the migration script — it does all of the steps below atomically and
copies every referenced local image, so no content can be silently lost:

```bash
python3 scripts/migrate.py 2 23          # migrate P2.23 from PART2_split/
python3 scripts/migrate.py 2 23 --force  # overwrite an existing qmd
python3 scripts/migrate.py 2 --all       # migrate every Part-2 source
```

What the script does:

1. Reads the source `.md` from `PART{N}_split/`.
2. Strips the leading `# Problem N. Title` H1 and demotes `# **Part N. …**`
   sub-h1s to `## Part N — …`.
3. Detects `status` from the filename suffix (`TBC` → `tbc`,
   `with Key/with Analysis` → `final`, otherwise `not-started`).
4. Detects `difficulty` from the `难度评级：★★★★☆` line (counts black stars).
5. Prepends YAML frontmatter and the Discord call-out callout box.
6. Copies every referenced local image from the source `images/` and
   `assets/` folders into the per-problem subfolder under `parts/partN/`.
7. Writes the result to `parts/partN/Problem_NN.qmd`.

After migration, polish the frontmatter (`topics`, `description`) and run:

```bash
python3 scripts/audit.py 2 23   # confirm nothing was lost
quarto preview                  # live-render to verify
```

## Auditing migrated problems

`scripts/audit.py` compares each `parts/partN/Problem_NN.qmd` against its
source `PART{N}_split/Problem_NN_*.md` and reports any image refs, solution
blockquotes, or local-file references that are present in source but
missing from the qmd. It also checks that every local image referenced by
the qmd actually exists on disk.

```bash
python3 scripts/audit.py                 # audit every Problem_NN.qmd
python3 scripts/audit.py 2 23            # audit just P2.23
python3 scripts/audit.py --strict        # exit 1 on any discrepancy
```

Run this **before every commit** that touches a problem file. The audit
catches the specific failure mode that motivated it: external-URL `<img>`
tags inside solution blockquotes silently dropped during transcription.

## Publishing to GitHub Pages

1. Create a public repo on GitHub (e.g., `icho2026-solutions`).
2. `git remote add origin git@github.com:<you>/icho2026-solutions.git`.
3. `git push -u origin main`.
4. On GitHub: **Settings → Pages → Source: GitHub Actions**.
5. Replace `CHANGE-ME` placeholders in `_quarto.yml` and `index.qmd` with your Discord invite URL and your repo URL.

## Per-problem printable PDFs (optional)

Uncomment the `pdf:` block in `_quarto.yml` and install a LaTeX engine (`quarto install tinytex`). Then `quarto render` produces both HTML and `.pdf` for every problem. Useful for class handouts.

## Adding a new problem

1. Drop the new `.qmd` into the right `parts/partN/` folder.
2. Set `status: draft` and fill `problem-id`, `difficulty`, `topics`.
3. Commit + push. Site rebuilds automatically.

## Reporting errors (for students)

Use the **Discord** link in any page's header or footer. Include:
- Problem code, e.g., `P2.07`.
- The specific step or equation you're commenting on.
