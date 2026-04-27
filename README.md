# Color is Destiny — or is it?

> A dueling scrollytelling visual data story about chess's oldest controversy:
> **does White's first-move advantage actually matter?**
>
> CSE 578 · Data Visualization Final Project

---

## The question

For 400 years, chess writers have argued that White's first move is a real advantage. Black has spent the same 400 years trying to disprove it. We tested both sides on **1,797,006 club-level Lichess games** (Elo 1000–1599) and built two scrollytelling essays that come to opposite conclusions — using the same data.

| Side | Claim | Headline number |
|---|---|---|
| **Side A — Color is Destiny** | White wins more. Always. Across every Elo band, every time control, and the strongest opening families. | **+3.9 pp** White edge across 1.8M games |
| **Side B — Color is Irrelevant** | Color barely moves the needle. Opening choice swings outcomes 5× harder, rating gap swings them 16× harder. | **+61.2 pp** spread from rating-diff alone |

Both sides are factually defensible. **Pick a side.**

---

## Live demo

The project is a static frontend — no backend required.

### Recommended (VS Code)
1. Open the repository folder in VS Code.
2. Install the **Live Server** extension (Ritwick Dey).
3. Right-click `viz/index.html` → **Open with Live Server**.
4. The browser opens at `http://127.0.0.1:5500/viz/index.html`.

### Alternative (any HTTP server)
```bash
cd viz
python -m http.server 8000
# then open http://127.0.0.1:8000/index.html
```

The dashboard fetches small pre-aggregated JSON files from `viz/data_color/`. Total payload **< 200 KB**. No network beyond CDN-hosted D3.

---

## Project structure

```
578trial/
├── README.md                        ← this file
├── .gitignore
├── Biweekly report 2.pdf            ← team progress reports
├── CSE578_Biweekly Report.pdf
├── Project_Sketches (1).pdf
└── viz/
    ├── index.html                   ← landing page
    ├── side_a.html                  ← "Color is Destiny" scrollytelling
    ├── side_b.html                  ← "Color is Irrelevant" scrollytelling
    ├── data_color/                  ← 13 pre-aggregated JSONs (committed)
    │   ├── 00_meta.json
    │   ├── A1_headline.json … A6_tug_of_war.json
    │   └── B1_color_share.json … B6_factor_variance.json
    └── scripts/
        └── preprocess_color.py      ← DuckDB pipeline
```

---

## Regenerating the data (optional)

The committed JSONs already work — you only need to do this if you want to change the slice (different Elo band, different month, etc.).

### 1. Download the source datasets

| Dataset | Source | Where it goes |
|---|---|---|
| Lichess June 2016 games (4.4 GB) | <https://www.kaggle.com/datasets/arevel/chess-games> | `data2/chess_games.csv` |
| All Chess Openings (940 KB) | <https://www.kaggle.com/datasets/alexandrelemercier/all-chess-openings> | `data1/openings.csv`, `data1/openings_fen7.csv` |

The pipeline only requires **chess_games.csv**. The opening reference dataset is provided for further exploration (it is not used by the canonical 12 charts).

### 2. Install Python dependencies

```bash
python -m pip install duckdb pandas
```

### 3. Run the pipeline

```bash
python viz/scripts/preprocess_color.py
```

This will:
- Stream the 6.25M-row CSV via DuckDB (no full load into RAM).
- Filter to Elo 1000–1599 (1,797,006 games).
- Emit the 13 chart JSONs into `viz/data_color/`.

Default runtime ≈ 7 seconds on a recent laptop.

### 4. Reload the dashboard

Refresh the browser. The charts pick up the new JSONs automatically.

---

## Visualization inventory

12 charts split across two scrollytelling essays. **9 distinct visualization techniques.**

### Side A — "Color is Destiny"
| # | Chart | Technique | Interactivity |
|---|---|---|---|
| A1 | The headline | horizontal bar with animated width | hover tooltip |
| A2 | Edge across Elo | multi-line with stroke-dash reveal | hover tooltip |
| A3 | Edge across time controls | stacked bar | hover tooltip · **click → cross-link to A6** |
| A4 | White's strongest weapons | treemap | hover tooltip |
| A5 | White checkmates Black | heatmap (YlOrRd on dark) | hover tooltip |
| A6 | **Tug of War** *(innovative)* | custom rope-and-knot metaphor | filter pills (all / time / Elo / opening) |

### Side B — "Color is Irrelevant"
| # | Chart | Technique | Interactivity |
|---|---|---|---|
| B1 | Out of 100 games | unit-chart waffle | hover per-square |
| B2 | Black's strongest defenses | grouped horizontal bar | hover tooltip |
| B3 | Most extreme opening edges | diverging bar (5 White + 5 Black) | hover tooltip |
| B4 | The opening spectrum | bubble scatter (log y) | hover · **click to pin label** |
| B5 | Win rate by rating gap | stacked bar (7 buckets) | hover tooltip |
| B6 | **Factor variance** *(innovative)* | custom-scaled bar with semantic annotation | sort toggle (impact / A–Z) |

**Innovative views (≥2 per rubric):**
1. **A6 — Tug of War.** Custom marks (ropes + knots) and channels (knot horizontal position = win-edge magnitude, color = direction) with interactive cut filters.
2. **B6 — Factor variance.** Computes the spread in White-win % each predictor produces, exposing that color is the *smallest* factor in the dataset. Includes a sort toggle and a semantic "← the runt" callout for the color factor.

---

## Tech stack

- **D3 v7** for all charts (loaded from CDN, no NVD3 / Vega-Lite / Highcharts).
- **DuckDB** for the preprocessing pipeline (Python).
- **Vanilla JS + IntersectionObserver** for scrollytelling reveal — no framework.
- **CSS Grid + custom dark theme**, no Bootstrap dependency.

---

## Team

| Member | Email |
|---|---|
| Mathew Abraham Palliambil | mpalliam@asu.edu |
| Basil Shibu Thomas | bthoma70@asu.edu |
| Asmit Datta | adatta18@asu.edu |
| Chandana Priya Srinivasa | csrini10@asu.edu |
| Kruthika Kadurhalli Raghu | kkadurha@asu.edu |
| Parth Jain | pjain121@asu.edu |

---

## Rubric checklist

| Requirement | Status |
|---|---|
| Genuinely controversial topic | ✅ — 400-year first-mover-advantage debate |
| Two contrasting scrollytelling essays | ✅ — `side_a.html`, `side_b.html` |
| ≥6 visualizations per side (12 total) | ✅ |
| ≥6 distinct visualization techniques | ✅ — 9 counted |
| ≥2 innovative views | ✅ — A6 Tug-of-War, B6 Factor variance |
| D3.js implementation | ✅ |
| Landing page with team + intro | ✅ — `index.html` |
| ≥25% animated/interactive | ✅ — 12 / 12 |
| Scrollytelling format | ✅ — IntersectionObserver reveal |
| Self-explanatory narration | ✅ — every chart paired with narrative copy |
| Cross-chart linkage | ✅ (extra credit) — A3 → A6 click-jump |

---

## Data license / source

Both datasets are from Kaggle and are publicly available:
- Arevel, "Chess Games (Lichess June 2016)" — <https://www.kaggle.com/datasets/arevel/chess-games>
- Alexandre Lemercier, "All Chess Openings" — <https://www.kaggle.com/datasets/alexandrelemercier/all-chess-openings>

The raw CSVs are excluded from this repository via `.gitignore` per the course rubric ("if your dataset is big, don't upload it to GitHub").
