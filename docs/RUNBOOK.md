# Runbook — day-to-day operations

This is the operational guide for the IChO 2026 Preparatory Problems solutions site. It assumes you've already cloned the repo and have Quarto + Python 3.10+ installed.

> **TL;DR cheat sheet** (the four commands you actually use):
> ```bash
> python3 scripts/migrate.py 2 NN          # add a new problem from source
> python3 scripts/audit.py [2 NN]          # verify content preserved
> quarto preview                            # live-reload editing
> git add … && git commit -m "…" && git push   # ship (CI auto-deploys)
> ```

---

## Prerequisites

- **Quarto ≥ 1.4** — check with `quarto --version`; tested with 1.6.42.
- **Python ≥ 3.10** — the scripts use stdlib only; no `pip install` needed.
- **Git** — repo is at `~/code/icho2026-solutions` and pushes to `git@github.com:archochen/icho2026pp.git`.
- **`gh` CLI** (optional) — handy for watching CI runs (`gh run watch`).
- The source archive lives in iCloud at `~/Library/Mobile Documents/com~apple~CloudDocs/学习工作/竞赛教学/IChO/2026年58届 乌兹别克/prep problems/PART2_split/` — the migration script reads from there.

---

## Adding a new problem from source

```bash
cd ~/code/icho2026-solutions
python3 scripts/migrate.py 2 NN          # creates parts/part2/Problem_NN.qmd
python3 scripts/audit.py 2 NN            # verify nothing dropped
```

What the migration does:

- Reads `PART2_split/Problem_NN_*.md` byte-for-byte.
- Strips the leading `# Problem N. Title` H1 (Quarto uses YAML `title:`).
- Demotes `# **Part N. …**` sub-h1s to `## Part N — …`.
- Detects `status` from the filename suffix:
  - `-with Key and Analysis - TBC.md` → `tbc`
  - `-with Key and Analysis.md` → `final` *(downgrade manually to `revised` or `draft` if not fully reviewed)*
  - no suffix → `not-started`
- Detects `difficulty` from the `难度评级：★★★★☆` line (counts black stars). Defaults to 3 if absent.
- Prepends frontmatter + Discord callout.
- Copies every referenced local image (`images/…` and `assets/…`) into `parts/part2/{images,assets}/`.

After migration, **always** run the audit. If audit reports issues, see [Troubleshooting](#troubleshooting) below.

Then optionally edit the new `.qmd` to:

- Tag `foad:` and `topics:` (see [Tagging a problem](#tagging-a-problem)).
- Adjust `status:` if the heuristic was wrong.
- Adjust `difficulty:` if the source had no ★ line and the default doesn't fit.
- Fill in `description:` (used in the dashboard hover and for SEO).

Commit + push:

```bash
git add parts/part2/Problem_NN.qmd parts/part2/images/ parts/part2/assets/
git commit -m "Add P2.NN — Title (status: …)"
git push
```

CI handles the rest: `quarto render` + `build-manifest.py` + GitHub Pages deploy in ≈ 60 s.

---

## Editing an existing problem

```bash
quarto preview                            # opens browser at http://localhost:NNNN
# edit parts/part2/Problem_NN.qmd in your editor; the page auto-reloads on save
python3 scripts/audit.py 2 NN             # before committing
git add parts/part2/Problem_NN.qmd
git commit -m "P2.NN: …"
git push
```

`quarto preview` watches every `.qmd` and re-renders the changed page in well under a second. Leave it running while you work.

---

## Tagging a problem

Open the `.qmd` and set the YAML frontmatter:

```yaml
foad: [mass-spectrometry, transition-metal-catalysis]
topics: [wilkinson-catalyst, hydrogenation, ms-fragments, allyl-cation]
```

**`foad:`** is **strict** — only the six canonical slugs from `_foad.yml` are valid:

- `mass-spectrometry`
- `kinetics`
- `thermodynamics`
- `transition-metal-catalysis`
- `photochemistry`
- `carbohydrate-chemistry`

A typo here will fail the audit. Use `foad: []` if the problem doesn't exercise any FoAD topic (classical inorganic stoichiometry puzzles often fall here).

**`topics:`** is **free-form** — any kebab-case slugs that describe the problem. Used for keyword filtering on the dashboard. Aim for 5–10 specific keywords (reaction names, named systems, compound classes). Avoid duplicating FoAD slugs.

After saving, the dashboard column updates on next render; the Syllabus page's cross-link updates on next manifest rebuild.

---

## Promoting a problem's status

`status:` lifecycle:

| Status | Meaning |
|---|---|
| `not-started` | No solution drafted. |
| `draft` | First pass, internally cross-checked, not peer-reviewed. |
| `revised` | Incorporates ≥ 1 round of external feedback. |
| `final` | Stabilized; no expected changes. |
| `tbc` | Specific contested step(s) flagged inline; awaiting verification. |

To promote (e.g. `tbc` → `revised` after resolving a contested step):

1. Edit the `.qmd`. Delete the inline `**🟡 TBC.**` marker line(s) in the affected solution blockquote(s).
2. Update `status:` in the frontmatter.
3. Audit + commit + push.

The page-level status badge (top of the rendered page) and the dashboard's Status column both update automatically.

---

## Marking sub-question uncertainty

When a single sub-question's answer is contested but others on the same page are fine, **do not** push the whole page to `tbc` (it overstates the issue). Instead:

1. Keep page-level `status:` accurate (often `revised`).
2. Add an inline marker at the top of the affected `**Solution (…)**` blockquote:

   ```markdown
   > **Solution (Q3 — MS fragment cations).**
   >
   > **🟡 TBC — short reason.** [What is uncertain | why | fallback or pointer to discuss.]
   >
   > [body unchanged]
   ```

The 🟡 prefix line renders as a visible yellow-dot warning at the top of that one solution. Remove the line when resolved.

See `parts/part2/Problem_21.qmd` (Q3 and Q4) for live examples.

---

## Configuring the Discord URL

Currently all references are placeholders `https://discord.gg/CHANGE-ME`. When you have the real invite:

```bash
git grep -l "discord.gg/CHANGE-ME" | xargs sed -i '' \
  's|https://discord.gg/CHANGE-ME|https://discord.gg/YOUR_REAL_INVITE|g'
git diff --stat
git commit -am "Set Discord invite URL"
git push
```

Touches:

- `_quarto.yml` (navbar + footer)
- `index.qmd` (top callout)
- every `parts/part2/Problem_NN.qmd` (per-page Discord callout)

`scripts/migrate.py` also has the placeholder hard-coded; update line `DISCORD_URL = "https://…"` there too so future migrations get the real URL.

---

## Auditing & validation

```bash
python3 scripts/audit.py              # audit every problem on the site
python3 scripts/audit.py 2 23         # audit just P2.23
python3 scripts/audit.py --strict     # exit 1 on any discrepancy (CI use)
```

What it checks per problem (`scripts/audit.py`):

1. **Image refs**: every image referenced in the source `.md` body (excluding Chinese sections) appears in the `.qmd`.
2. **Solution blockquote labels**: every `> **Solution (Qn — …)**` in source appears in `.qmd` (fuzzy match on math).
3. **Local image files**: every local image referenced in the `.qmd` exists on disk under `parts/part2/{images,assets}/`.
4. **FoAD slug validity**: every entry in the `foad:` frontmatter field is in the canonical 6-item vocabulary.

If the audit reports issues, see [Troubleshooting](#troubleshooting).

---

## Local render & deploy

```bash
quarto render                         # one-shot rebuild → _site/
python3 scripts/build-manifest.py     # update _site/manifest.json (needed for syllabus cross-links)
```

For production deploy: just `git push`. The GitHub Actions workflow at `.github/workflows/publish.yml` runs the same two commands and ships `_site/` to GitHub Pages.

URLs:
- Production: <https://archochen.github.io/icho2026pp/>
- Repo: <https://github.com/archochen/icho2026pp>
- CI runs: `gh run list --repo archochen/icho2026pp --limit 5`
- Watch latest: `gh run watch $(gh run list --repo archochen/icho2026pp --limit 1 --json databaseId -q '.[0].databaseId')`

---

## Troubleshooting

### Audit: "missing Solution blockquote: q… — …"

Source `.md` has a solution label that isn't found in the `.qmd`. Two cases:

- **Accidental drop** — you missed copying a solution while editing. Fix: copy it back.
- **Deliberate label change** — you intentionally renamed (e.g. `QN` → `Q1`). Fix: update the source `.md` to match so they're in sync, OR ignore the warning (audit will keep flagging until they match).

### Audit: "local image referenced but not on disk: …"

The `.qmd` mentions an image at `images/foo.jpg` or `assets/bar.png` but the file isn't under `parts/part2/`. Either remove the reference or copy the file from `PART2_split/`.

### Audit: "unknown foad slug: '…'"

Typo or out-of-vocab slug in `foad:`. Compare exactly against `_foad.yml`.

### TOC sidebar is empty / Q-heading missing

The `q-headings` Lua filter triggers on blockquotes that start with `**Solution (Qn — Topic).**` and inject an `<h2>` above the preceding numbered question. If the heading doesn't appear:

- Check the label has the literal text `Solution (` followed by content followed by `)`.
- Check there's an `OrderedList` (numbered question line) immediately before the blockquote.
- Math inside the label (e.g. `$T_\mathrm{m}$`) is OK; the filter walks the AST to preserve Math nodes.

### Image too small or too large

`styles.scss` rule: `max-width: min(720px, 100%); width: auto`. Images cap at 720 px wide; smaller images stay at natural size.

`zoom: 1 !important` overrides the inline `style="zoom:50%"` that MinerU OCR sometimes attaches.

For a specific image that needs a different size, edit its inline `<img ...>` tag in the `.qmd` and add an explicit width or wrap it in a div with a custom class.

### Chinese content appearing in HTML

The `hide-cn-sections` Lua filter truncates the document at the first `<h1>` or `<h2>` whose text contains one of:

`中文版` · `Chinese translation` · `教学点评` · `解题分析` · `相对丰度表`

If Chinese content leaks through, check the section headers exactly start with `#` or `##` and contain one of those markers. Plain paragraphs containing Chinese inside the visible (English) section are not stripped — only headings trigger the truncate.

### CI build fails

```bash
gh run list --repo archochen/icho2026pp --limit 5
gh run view <run-id> --log-failed | tail -40
```

Common causes:
- Quarto version mismatch (workflow pins 1.6.42; bump if needed)
- Python 3 not invoked correctly (the workflow uses the runner's default `python3`)
- A new Lua filter throwing an error (try `quarto render` locally first)
