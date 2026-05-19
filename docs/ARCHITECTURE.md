# Architecture — design decisions and why

This is the "why" doc. Read [`RUNBOOK.md`](RUNBOOK.md) first for the "how"; come here when you need to understand a non-obvious choice.

---

## Goals & non-goals

**Goals**
- Single source of truth: Markdown / Quarto `.qmd` files render to HTML.
- Auto-publish on every push (zero manual deploy).
- Per-problem status visible at a glance (dashboard + on-page badge).
- Bilingual source preserved for the maintainer; HTML output is English-only for students.
- Syllabus-aligned: every problem visibly tagged with the FoAD it exercises.
- Student feedback channel: Discord link from every page.

**Non-goals**
- Inline web comments — Discord covers this.
- WYSIWYG editing.
- Per-user accounts or progress tracking.
- Part 3 coverage (lab practicals) — explicitly out of scope.
- Per-problem PDF (wired in `_quarto.yml` but commented; enable when handouts are needed).

---

## High-level pipeline

```
parts/part2/Problem_NN.qmd  ── quarto render ──►  _site/parts/part2/Problem_NN.html
                                       │
                                       └─ build-manifest.py ──►  _site/manifest.json
                                                                       │
                                                                       └─ fetched by syllabus.html JS
```

Build steps (local or in CI):

1. `quarto render` — renders every `.qmd` to HTML using the three custom Lua filters.
2. `python3 scripts/build-manifest.py` — emits `_site/manifest.json` with per-problem frontmatter.
3. `_site/` is uploaded to GitHub Pages (via `.github/workflows/publish.yml` in CI; local preview just serves it directly).

---

## Stack

- **Quarto** — static site generator chosen for native KaTeX + `mhchem` chemistry rendering, listing-based dashboards, and good support for scientific content. Version pinned to 1.6.42 in CI.
- **GitHub Pages** — free hosting, no infra to maintain.
- **GitHub Actions** — auto-render and deploy on push to `main`.
- **Discord** — student feedback. The site links to a Discord invite from every page; no inline comments.
- **No JS framework, no build tool beyond Quarto + a single Python script.**

---

## Custom Quarto extensions (Lua filters)

Three filters live in `_extensions/` and are registered in `_quarto.yml` under `format: html: filters:`.

### `_extensions/status-badge/`

Reads `status:` from the problem's frontmatter and injects a coloured pill badge at the top of the rendered page. Slug → colour mapping is in `styles.scss`. Status enum: `not-started` / `draft` / `revised` / `final` / `tbc`.

### `_extensions/q-headings/`

For every blockquote whose first paragraph starts with `**Solution (Qn — Topic).**`, synthesises an `<h2>` heading with text `Qn — Topic` and inserts it before the preceding `OrderedList` (the question text). This populates the right-hand TOC sidebar with one entry per sub-question — essential for navigating long problems like P2.23 (9 sub-questions) and P2.24 (9 sub-questions).

**Why walk the AST instead of stringify-and-reparse:** `pandoc.utils.stringify` discards `$` math delimiters, so re-parsing `"Q24.2 — Effect on T_\mathrm{m}"` yields literal text instead of a Math node. The filter walks the inline AST directly to preserve Math / Emph / Code inlines verbatim.

**Slug generation:** the synthesised heading also needs a URL-safe anchor id. The slugifier strips em-dash / en-dash UTF-8 bytes, drops high-bit bytes, and collapses non-`[a-z0-9]` runs to single hyphens. See `slugify()` in `q-headings.lua`.

### `_extensions/hide-cn-sections/`

Truncates the document at the first header whose text contains one of:

`中文版` · `Chinese translation` · `教学点评` · `解题分析` · `相对丰度表`

Every block from that header onward is dropped from HTML output. Source `.qmd` content is preserved — only HTML output is affected. The maintainer reads the full bilingual source; students see English only.

**Why truncate-at-first-marker, not a level-aware skip:** the user's source structure has mixed heading levels inside the Chinese block (`## 中文版` at h2, then `# 第 N 题` at h1 inside the same block). A level-comparison skip exits the hidden range when it encounters a shallower heading, breaking the intent. Truncate-at-first-marker works because Chinese content is always contiguous at the *end* of each problem file.

---

## Manifest pipeline

`scripts/build-manifest.py` runs after `quarto render` and produces `_site/manifest.json`: a JSON array with one entry per problem, carrying full frontmatter (title, problem-id, status, difficulty, foad, topics, date, description, path).

The Syllabus page's per-FoAD "On this site" cross-link JS fetches `manifest.json` to populate each `<div data-foad-list="…">`.

**Why a custom manifest:** Quarto's own `_site/listings.json` only contains URL strings for each listing item — not the full frontmatter. We need foad metadata to drive the syllabus cross-links, so we generate our own.

The manifest is regenerated every time. It's not tracked in git (lives in `_site/`, which is gitignored). CI runs `build-manifest.py` after `quarto render` in `.github/workflows/publish.yml`.

---

## The FoAD canonical vocabulary

`_foad.yml` at the repo root defines the six syllabus slugs:

`mass-spectrometry` · `kinetics` · `thermodynamics` · `transition-metal-catalysis` · `photochemistry` · `carbohydrate-chemistry`

Each entry has a short display label (`MS`, `Kinetics`, `Thermo`, `TM-cat`, `Photochem`, `Carbo`) and a brand colour. The vocabulary is mirrored in:

- `scripts/audit.py` — `FOAD_VOCAB` set, used to validate frontmatter values.
- `styles.scss` — per-slug `.foad-…` colour classes.
- `index.qmd` inline JS — slug → short-label map for badge decoration.
- `syllabus.qmd` — one `<div data-foad-list="slug">` per topic, plus the JS that fetches the manifest and populates each div.

**Update protocol:** if the IChO syllabus changes (an FoAD topic is added or renamed), update `_foad.yml` first, then propagate to all four mirrors. The audit script will catch any frontmatter referencing a stale slug.

---

## Scripts

### `scripts/migrate.py`
Source `.md` → `.qmd` converter. Deterministic byte-level copy with regex transforms (strip Problem H1, demote `**Part N**` sub-h1s, demote Chinese-section h1s). Detects status from the filename suffix and difficulty from the `难度评级` ★ count. Prepends YAML frontmatter + Discord callout. Copies every referenced local image into the per-problem subfolder.

**Why a deterministic script and not manual transcription:** the original failure mode that prompted this script (P2.24) was a 5-image silent drop during hand-copy. The script eliminates the human step.

### `scripts/audit.py`
Verifies content preservation post-migration. Four checks:
1. Every image ref in source `.md` (English part only) appears in `.qmd`.
2. Every solution blockquote label in source appears in `.qmd` (fuzzy on math).
3. Every local image ref in `.qmd` exists on disk.
4. Every `foad:` value in `.qmd` is in `FOAD_VOCAB`.

Run after every edit, before every commit, in CI as a guard (`--strict` exits non-zero on any issue).

### `scripts/build-manifest.py`
Writes `_site/manifest.json` after `quarto render`. Frontmatter parser is hand-rolled with regex (no pyyaml dependency) — fast and stdlib-only.

---

## File structure

```
icho2026-solutions/
├── _quarto.yml                  # site config, navbar, KaTeX/mhchem, filter registration
├── _foad.yml                    # canonical FoAD vocabulary (6 slugs)
├── styles.scss                  # custom theme + status/foad badges
├── index.qmd                    # homepage dashboard (Quarto listing)
├── syllabus.qmd                 # Part 1 syllabus + per-FoAD cross-links
├── about.qmd                    # scope statement, how-to-read, error reporting
├── _extensions/                 # custom Quarto extensions
│   ├── status-badge/            #   per-page status pill
│   ├── q-headings/              #   auto-inject Q-headings from solution blockquotes
│   └── hide-cn-sections/        #   strip Chinese sections from HTML
├── parts/
│   └── part2/                   # the Part 2 problems (the site's main content)
│       ├── _metadata.yml        #   part: 2  (inherited by every problem in this folder)
│       ├── Problem_NN.qmd
│       ├── images/              #   per-problem JPG scheme images
│       └── assets/              #   per-problem PNG mechanism overlays
├── scripts/                     # automation
│   ├── migrate.py
│   ├── audit.py
│   └── build-manifest.py
├── docs/                        # this folder
│   ├── RUNBOOK.md
│   ├── TODO.md
│   └── ARCHITECTURE.md
├── README.md
└── .github/workflows/publish.yml
```

There is intentionally **no** `parts/part1/` or `parts/part3/` directory.

---

## Significant design decisions

### IA: site is a Part 2 solutions site, not a "three-parts-of-problems" site

The IChO booklet has three parts; only one is problems. Part 1 is the syllabus (Fields of Advanced Difficulty + reference tables); Part 3 is lab practicals.

Earlier iterations of the site had `parts/part{1,2,3}/` directories with placeholder `.qmd` files and a navbar showing all three — that misled visitors and produced broken links. The current IA names what's actually there: **Home** (Part 2 problems dashboard), **Syllabus** (Part 1 reference), **About** (scope statement naming Part 3 as out of scope).

Do not recreate `parts/part1/` or `parts/part3/` placeholder folders.

### Chinese content hidden via Lua filter, not Quarto callouts

`::: {.content-hidden when-format="html"}` was the initial attempt but renders inconsistently inside blockquotes across themes. The custom Lua filter is more predictable and doesn't depend on Quarto's evolving conditional-content semantics.

### Per-problem inline TBC marker, not page-level status alone

Page-level `status: tbc` says "this page has at least one unresolved answer" but doesn't pinpoint which. For sub-question uncertainty, a bold inline marker (`**🟡 TBC.** [reason]`) at the top of the affected solution blockquote names the specific sub-question. Two-tier signal: page status + sub-question marker. Easy to grep, easy to remove when resolved.

Chosen over (a) modifying the solution label (breaks audit's label-match check) and (b) Quarto callout inside blockquote (renders unevenly).

### `topics:` and `foad:` are separate fields

`foad:` answers "which FoAD syllabus units?" — strict, fixed 6-slug vocabulary, audit-validated. Drives study-by-syllabus workflows.

`topics:` answers "what keywords describe this problem?" — free-form, flexible, drives keyword search.

Combining them into one field (a single `topics:` list with FoAD slugs first) was considered but rejected: different semantics deserve different fields, and separating them allows the dashboard to visually elevate the FoAD badges (coloured pills) while keeping topics as plain text.

### Image size policy: cap, don't enlarge

`max-width: min(720px, 100%); width: auto`. Wide MinerU-OCR-rendered schemes shrink to fit the column; small structural diagrams (≤ 250 px natural) keep their natural pixel size — no blurry up-scaling.

The previous policy (`width: min(720px, 100%)`) blew small images up by 4–6×. Trade-off: small images now appear small on a wide screen. If a specific image needs enlarging, edit its inline `<img>` tag or wrap it in a div with a custom class.

The `zoom: 1 !important` override neutralises the inline `style="zoom:50%"` (or 33%, 25%) that MinerU embeds during PDF-to-markdown conversion.

### Manifest is generated, not committed

`_site/manifest.json` is regenerated on every render. It's gitignored along with the rest of `_site/`. CI builds it during deploy. There's no canonical "manifest file at repo root" because keeping it in sync with the source files would be a tracking nightmare.

### Source archive lives in iCloud

The original Markdown sources (`PART2_split/Problem_NN_*.md`) live in iCloud Drive at the user's local path. The repo at `~/code/icho2026-solutions` is **outside iCloud** to avoid the iCloud-sync vs. git collision that breaks Quarto's file watcher and produces rename-on-conflict files.

The migration script reads from the iCloud path. If that path changes (different machine, different OS user), update `ICLOUD_ROOT` in both `scripts/migrate.py` and `scripts/audit.py`.

---

## CI/CD

`.github/workflows/publish.yml`:

```yaml
build:
  - actions/checkout@v4
  - quarto-dev/quarto-actions/setup@v2 (version: 1.6.42)
  - quarto render
  - python3 scripts/build-manifest.py
  - actions/upload-pages-artifact@v3 (path: _site)

deploy:
  - actions/deploy-pages@v4
```

Trigger: push to `main`. Total build + deploy: ≈ 60 s.

GitHub Pages settings: **Source = GitHub Actions** (set once via `gh api -X POST repos/.../pages -f build_type=workflow`; persistent thereafter).

---

## What to read next

- **Day-to-day operations**: [`RUNBOOK.md`](RUNBOOK.md).
- **Pending work and known issues**: [`TODO.md`](TODO.md).
- **Repo overview / new-contributor onboarding**: [`../README.md`](../README.md).
