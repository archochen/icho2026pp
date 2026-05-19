# IChO 2026 Preparatory Problems — Solutions

Worked solutions and pedagogical analyses for the 30 theoretical problems (Part 2) of the **58th IChO (Uzbekistan, 2026)** Preparatory Problems, plus a reference page for the Part 1 syllabus (Fields of Advanced Difficulty). Markdown is the single source of truth; Quarto builds the website on every push.

🌐 **Live:** <https://archochen.github.io/icho2026pp/>

---

## Where to find more

| Doc | Read this when… |
|---|---|
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | …you want to **do** something (migrate, edit, tag, audit, troubleshoot). |
| [docs/TODO.md](docs/TODO.md) | …you want to know what's **pending** (unmigrated problems, TBC items, open contests). |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | …you want to know **why** a thing is the way it is (filter design, IA, FoAD vocabulary). |
| The Site's [About page](https://archochen.github.io/icho2026pp/about.html) | …you're a student wondering what's covered. |

---

## Stack

- **Quarto ≥ 1.4** for the static site (KaTeX + `mhchem` for chemistry, custom Lua filters for status badges, auto-injected Q-headings, and Chinese-section hiding).
- **GitHub Pages** for hosting; **GitHub Actions** for auto-deploy on push.
- **Python 3 (stdlib only)** for the three helper scripts in `scripts/`.
- **Discord** for student feedback (one invite linked from every page).

---

## Quick start

```bash
cd ~/code/icho2026-solutions     # repo lives OUTSIDE iCloud
quarto preview                    # live-reload editing
```

Add a new problem from the iCloud source archive:

```bash
python3 scripts/migrate.py 2 NN   # source.md → parts/part2/Problem_NN.qmd
python3 scripts/audit.py 2 NN     # verify no content dropped
git add -A && git commit -m "Add P2.NN — Title (status: …)" && git push
```

CI renders and deploys in about 60 seconds.

---

## Problem frontmatter at a glance

```yaml
---
title: "P2.21 — Catalyst C"
problem-id: 21
status: tbc                                          # not-started | draft | revised | final | tbc
difficulty: 3                                        # 0–5
foad: [mass-spectrometry, transition-metal-catalysis]   # canonical, validated by audit
topics: [wilkinson-catalyst, hydrogenation, …]       # free-form keywords
date: "2026-05-18"
description: ""
---
```

The **`foad:`** field is constrained to the six canonical slugs in [`_foad.yml`](_foad.yml); the **`topics:`** field is free-form. See [docs/RUNBOOK.md § Tagging a problem](docs/RUNBOOK.md#tagging-a-problem) for full details.

---

## Status lifecycle

| Status | Meaning |
| ------ | ------- |
| `not-started` | No solution drafted yet. |
| `draft` | First pass complete, internally cross-checked, **not** peer-reviewed. |
| `revised` | Incorporates at least one round of external feedback. |
| `final` | Answer key and pedagogical analysis stabilized; no expected changes. |
| `tbc` | One or more sub-questions are contested and flagged inline; awaiting verification. |

Page-level status drives the colored pill badge atop each problem page and the Status column on the dashboard. For sub-question-level uncertainty, add an inline **🟡 TBC** marker at the top of the affected solution blockquote (see existing examples in `parts/part2/Problem_21.qmd` Q3 + Q4).

---

## Repo layout

```
icho2026-solutions/
├── _quarto.yml              # site config (navbar, KaTeX/mhchem, filter registration)
├── _foad.yml                # canonical FoAD vocabulary
├── styles.scss              # custom theme + status/foad badges
├── index.qmd                # homepage dashboard (Quarto listing)
├── syllabus.qmd             # Part 1 syllabus + per-FoAD cross-links
├── about.qmd                # scope statement
├── _extensions/             # custom Quarto extensions (Lua filters)
│   ├── status-badge/
│   ├── q-headings/
│   └── hide-cn-sections/
├── parts/part2/             # the Part 2 problems
│   ├── _metadata.yml        # part: 2 (inherited)
│   ├── Problem_NN.qmd
│   ├── images/
│   └── assets/
├── scripts/                 # migrate / audit / manifest
├── docs/                    # RUNBOOK, TODO, ARCHITECTURE
├── README.md
└── .github/workflows/publish.yml
```

There is intentionally **no** `parts/part1/` (Part 1 is a single syllabus page at the root) and no `parts/part3/` (lab practicals are out of scope).

---

## Reporting errors (for students)

Use the **Discord** link in any page's header or footer. Include:

- Problem code, e.g. **P2.21**
- Sub-question number, e.g. **Q3.2**
- The specific step or equation, quoted

Issues are also welcome on the [GitHub repo](https://github.com/archochen/icho2026pp/issues) if you prefer.
