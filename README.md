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

For each `.md` in the iCloud source tree:

1. Copy the file body into `parts/part2/Problem_NN.qmd`.
2. Strip the leading `# Problem N. …` H1 (Quarto uses the YAML `title:`).
3. Add the frontmatter block.
4. Copy referenced images into `parts/part2/images/` so the existing `<img src="images/…">` references keep working.
5. `quarto preview` to verify.

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
