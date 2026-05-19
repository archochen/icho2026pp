# TODO — pending work and known issues

A living list of everything that's incomplete, contested, or pending. Update when a state changes. Last refreshed: 2026-05-19.

---

## 1. Open placeholders

| What | Where | Action |
|---|---|---|
| Discord invite URL | `_quarto.yml`, `index.qmd`, every `parts/part2/Problem_NN.qmd`, `scripts/migrate.py` | Find-and-replace `discord.gg/CHANGE-ME` once the invite is ready. See [RUNBOOK § Configuring the Discord URL](RUNBOOK.md#configuring-the-discord-url). |

---

## 2. Problems not yet migrated (22 of 30)

Source files in `PART2_split/`; migrate via `python3 scripts/migrate.py 2 NN`.

> **Note on source state.** The project memory says Part 2 is "30/30 compiled, solved, bilingual, cleaned" (as of 2026-04-30), but most source filenames below still lack the `- with Key and Analysis` suffix. Verify in iCloud before migrating — the migration script's status auto-detection reads the filename suffix, so a missing suffix lands the new problem as `not-started`.

| # | Title | Source filename suffix today | Expected initial status |
|---|---|---|---|
| 05 | Haber-Bosch process | (none) | `not-started` |
| 06 | Hydrogen fuel | (none) | `not-started` |
| 07 | 150 Years of Urease | (none) | `not-started` |
| 08 | Step-by-step | (none) | `not-started` |
| 09 | Host-guest chemistry of cucurbiturils as Uzbek hospitality | (none) | `not-started` |
| 10 | Prebiotic life | (none) | `not-started` |
| 11 | Fluorescence, phosphorescence and quenching | (none) | `not-started` |
| 12 | Photoacids | (none) | `not-started` |
| 13 | Interested in micelles | (none) | `not-started` |
| 14 | The basics of Metal-Organic Frameworks | (none) | `not-started` |
| 15 | Microscopy in chemistry | (none) | `not-started` |
| 16 | Kinase inhibitors | (none) | `not-started` |
| 18 | Inositol | (none) | `not-started` |
| 19 | Carbohydrates as chiral pools | (none) | `not-started` |
| 20 | Pacman, Hangman, Cageman | (none) | `not-started` |
| 22 | Transition metals in organometallic catalysis | (none) | `not-started` |
| 25 | The equilibria in DNA | (none) | `not-started` |
| 26 | Sensing of acetaldehyde | (none) | `not-started` |
| 27 | Archaeal metabolism | (none) | `not-started` |
| 28 | Non-archea-typal form of life | (none) | `not-started` |
| 29 | Archaea-ology | (none) | `not-started` |
| 30 | Pilaf ingredients | (none) | `not-started` |

After migration, **always tag** the new problem with FoAD + topics. Likely FoAD assignments based on titles alone:

- **MS (FoAD #1)** candidates: P2.08 *(Step-by-step?)*, P2.16 *(Kinase inhibitors)* — TBD
- **Kinetics (FoAD #2)** candidates: P2.07 *(Urease)*, P2.16 *(Kinase inhibitors)* — likely both
- **Thermodynamics (FoAD #3)** candidates: P2.05 *(Haber-Bosch)*, P2.06 *(Hydrogen fuel)*, P2.25 *(DNA equilibria)* — strong
- **Transition metal catalysis (FoAD #4)** candidates: P2.22 *(TM in organometallic catalysis)* — definite
- **Photochemistry (FoAD #5)** candidates: P2.11 *(Fluorescence/phosphorescence/quenching)*, P2.12 *(Photoacids)* — definite
- **Carbohydrate chemistry (FoAD #6)** candidates: P2.18 *(Inositol)*, P2.19 *(Carbohydrates as chiral pools)* — definite

Tag heuristics: only assign a FoAD slug if the problem actually exercises that syllabus topic in depth (not just passing mention). Default to `foad: []` when in doubt.

---

## 3. Migrated problems — current state (8 of 30)

| # | Title | Status | Difficulty | FoAD | Open items |
|---|---|---|---|---|---|
| 01 | Khoja Nasreddin is now a chemist | `final` | 5 | — | — |
| 02 | Avicenna | `final` | 4 | — | Review the migrated bilingual content for accuracy |
| 03 | Unusual inorganic synthesis | `tbc` | 5 | — | **Q3 mass-ratio discrepancy** — see §4 |
| 04 | Nanozymes | `tbc` | 3 | `kinetics` | Source had no ★ rating; difficulty default may be too low. Review TBC markers in source |
| 17 | Carbohydrate chemistry | `tbc` | 3 | `carbohydrate-chemistry` | Status was migrated as `not-started`; manually set to `tbc`. Review for accuracy |
| 21 | Catalyst C | `tbc` | 3 | `mass-spectrometry`, `transition-metal-catalysis` | Q21.3 / Q21.4 / Q21.6 resolved 2026-05-19 (cumyl-cation precursor); Q21.5 / Q21.7 / Q21.8 still need independent review |
| 23 | HAT and XAT (HalAT) | `tbc` | 4 | `mass-spectrometry`, `transition-metal-catalysis` | Multiple steps; Q3 OS/CN/VE direction is the subtlest |
| 24 | Anticancer complexes | `tbc` | 4 | — | Q24.6 / Q24.7 synthesis steps need verification |

---

## 4. Sub-question TBC items requiring human review

These are the inline-flagged contested points. The page-level `status: tbc` reflects them; the inline `🟡 TBC` marker pinpoints which sub-question.

### P2.03 — Q3 (identification of A1–A4, B, X)

**The mass ratio "1.613 g B from 1.000 g X" doesn't match selenate(VI).**
- Hot-atom chemistry (Szilard–Chalmers) demands selenate(VI) so the daughter ends up as $\mathrm{BrO_4^-}$. Predicted ratio: $w(\mathrm{SeO_4^{2-}/Se}) = 1.79$, materially larger than 1.613.
- The stated 1.613 fits **selenite** ($\mathrm{HSeO_3^-}$: 1.598) or $\mathrm{H_2SeO_3}$: 1.611) almost exactly.
- Current resolution in the .qmd: keep B = $\mathrm{^{83}SeO_4^{2-}}$ on chemistry grounds; note the discrepancy.

**Possible resolutions for the maintainer to evaluate:**
1. The quoted ratio refers to a *selenite* intermediate that forms before full ozonisation (B is then a transient $\mathrm{HSeO_3^-}$, not the final selenate).
2. The problem statement has an internal arithmetic inconsistency (unlikely but possible — flag in answer key feedback if so).
3. A different B identity entirely that we've missed.

**Location**: `parts/part2/Problem_03.qmd` Q3 solution.

### ~~P2.21 — Q21.3 / Q21.4 / Q21.6 (hydrogenation product structure)~~  **RESOLVED 2026-05-19**

Definitive answer (per maintainer): **(1,1-dimethylbutyl)benzene** = 2-methyl-2-phenylpentane = $\mathrm{Ph\text{-}C(CH_3)_2\text{-}CH_2CH_2CH_3}$ (CAS 1985-58-6).

The earlier candidates (1-butyl-4-ethylbenzene, 1-ethyl-4-isobutylbenzene) both fit the m/z 119 base peak by α-cleavage but predicted a *moderate* m/z 147 from methyl-loss α-cleavage on the ethyl side — whereas the spectrum shows m/z 147 as a *trace*. The tertiary benzylic structure correctly predicts m/z 147 to be nearly absent because the cumyl-cation channel (loss of ·n-Pr) is overwhelmingly preferred (Stevenson's rule + cumyl's exceptional cation stability).

Sub-question updates committed:

- **Q21.3** — cation drawings: m/z 119 = **cumyl cation** $\mathrm{Ph\text{-}C(CH_3)_2^+}$ (was: 4-ethylbenzyl/ethyl-tropylium). m/z 91 = tropylium via secondary loss of $\mathrm{C_2H_4}$ from cumyl⁺ (ring expansion 6→7). m/z 41 = allyl from complementary $\mathrm{C_3H_7^+}$ minus $\mathrm{H_2}$. The "two different aromatic rings" clue is now beautifully precise: 91 is a 7-membered tropylium ring, 119 contains a 6-membered benzene ring with sp³ α-cation.
- **Q21.4** — product, symmetry, MS rationalisation, substrate compatibility all rewritten.
- **Q21.6** — minor isomerization product D re-derived: $\mathrm{Ph\text{-}C(CH_3)_2\text{-}CH=CH\text{-}CH_3}$ = 4-methyl-4-phenylpent-2-ene ($\mathrm{C_{12}H_{16}}$). The cumyl α-C is quaternary (no α-H), so the C=C halts at the internal isomer. (Previous answer was a stale "Ph₂CH–CH=C(CH₃)–CH₃" carryover from the long-retired diphenylalkene assignment.)

Inline `🟡 TBC` markers on Q21.3 and Q21.4 removed. Page-level status remains `tbc` until other sub-questions (Q21.5, Q21.7, Q21.8) are independently reviewed — promote to `revised` when ready.

### P2.23 — Q3 (OS/CN/VE for HAT/XAT products)

The non-obvious point: HAT to a metal-oxo (M=O → M–OH) **reduces** the metal by one (OS decreases), while XAT to the metal centre **oxidises** it by one (OS increases). The intuition "the metal gained a bond → OS increased" is wrong for HAT to an oxo ligand because the H attaches to O, not to the metal.

The current solution states this correctly with the rationale, but the OS direction is the kind of thing that benefits from a second-opinion review.

**Location**: `parts/part2/Problem_23.qmd` Q3 solution.

### P2.24 — Q24.6 / Q24.7 (SN-38 synthesis)

The Curran/Comins-style east block (Q24.6) and Knorr quinolone + Pd-Heck west block + final coupling (Q24.7) are long synthesis sequences. The current write-ups identify A→H and J→O+SN-38 step-by-step but rely on textbook precedent rather than per-step verification against the original literature.

**Location**: `parts/part2/Problem_24.qmd` Q6 + Q7 solutions.

---

## 5. Stylistic / content polishing

Items that don't block but would improve the site once the core migration is done:

- **Fill in `description:` fields** on all problems. Currently most are empty `""`. The description shows in the dashboard hover and is used for SEO + social previews.
- **Review difficulty ratings**. The migration script reads `难度评级：★★★★☆` from the source's analysis section. For sources without that line (P2.04 today), it defaults to 3, which may understate.
- **Review the `topics:` lists** on P2.02 and P2.17 — I picked them from source content but they may need refinement after a closer read.

---

## 6. Future enhancements (low priority)

- **Full-text search** — Quarto's built-in `search` already covers most use cases; verify it indexes solution body text correctly once more problems land.
- **Per-FoAD filter buttons** on the dashboard (visible "FoAD: MS / Kinetics / …" chips that filter the table). The current filter input box works but is keyword-driven, not button-driven.
- **Cross-link from problem page back to syllabus**. Currently the FoAD badges at the top of each problem are just decorative. They could link to `syllabus.qmd#section-NAME`.
- **A "coverage matrix" on the syllabus page** — small grid showing which problems hit which FoAD topic, for instant gap-analysis.
- **Per-problem PDF** via Quarto's PDF output. Already commented in `_quarto.yml`; uncomment + `quarto install tinytex` when handouts are needed.
- **Migrate Part 3 lab practicals** *(currently flagged out of scope)* — re-enable `parts/part3/` and add a `Practicals` navbar entry if the scope ever expands.
