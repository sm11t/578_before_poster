# Project Report — Color is Destiny, or is it?

> CSE 578 Data Visualization · Final Project Report
> Topic: Does White's first-move advantage in chess actually matter at the level where most chess is played?

---

## 1 · The topic and why it qualifies as controversial

For 400 years, chess writers have argued whether White's first-move advantage is a real, persistent edge or a marginal effect that disappears once both sides understand opening theory. Steinitz, Lasker, Capablanca, and modern engine-driven analysts have all weighed in on opposite sides of this question. Chess.com publishes regular "is the gap closing?" pieces; Lichess analyses contradict them; FIDE classical statistics differ again. The debate is **alive, unresolved, and genuinely two-sided**.

We chose this topic because it satisfies the rubric's "controversial topic" requirement without being a banned area (no AI/GenAI, no COVID, no GOAT debates). It is also a debate where the data does not crown a clear winner — both perspectives are factually defensible — which makes a dueling-story format the right vehicle.

The one-line topic: **Does the colour you got dealt actually decide your chess game?**

---

## 2 · The dataset and why we filtered it

### Source

| Dataset | Source | Size | What we use it for |
|---|---|---|---|
| Lichess June 2016 standard games | https://www.kaggle.com/datasets/arevel/chess-games | 6.25M rows · 4.4 GB | Every chart |
| All Chess Openings | https://www.kaggle.com/datasets/alexandrelemercier/all-chess-openings | 1.8k rows · 745 KB | Reference; not used by canonical charts |

### Why we filter to Elo 1000–1599

Three reasons:

1. **It's where most chess actually happens.** This Elo band contains 1,797,006 of the 6.25M games — almost a third — and represents the vast middle of the Lichess player population. A finding here generalises to the typical user experience.
2. **It avoids the data-thin tails.** Above Elo 2200 we have only ~33,000 games, far too noisy for reliable per-opening per-Elo cuts. Below Elo 1000 we have ~2,000 games, even noisier and dominated by abandoned games.
3. **It is the level where the rubric-relevant audience plays.** Our story should be intelligible and actionable for a typical reader, not for grandmasters. Filtering to club-level keeps the narrative grounded.

The filter is documented on the index page, in `00_meta.json`, and in this report.

---

## 3 · The two stories

### Side A — "Color is Destiny" (`side_a.html`)

**Thesis.** White's first-move advantage is real, persistent, and visible at every cut of the data. Across 1.8M games White wins 50.4%, Black wins 46.5%, and the gap (+3.9 percentage points) does not vanish when you slice by Elo, by time control, or by opening. White-favouring sharp openings (Bishop's, Italian, Philidor) hand White over 53% wins; the heatmap of who delivers checkmate skews toward White at every cell. The first-move advantage is not a myth.

**Money number.** +3.9 pp White edge across all 1,797,006 games.

### Side B — "Color is Irrelevant" (`side_b.html`)

**Thesis.** Yes, +3.9 pp is real. It is also tiny. The most popular response in chess (the Sicilian Defense, 152k games at this level) is one that **Black** wins more often. The opening you choose can swing your win rate by 19 percentage points. The rating gap between you and your opponent can swing it by 61. Color is the smallest predictor of outcome we can find in the data — useful to know, but irrelevant to who actually wins your next game.

**Money number.** Spread comparison: color = 3.9 pp, time control = 0.4 pp, Elo = 0.9 pp, opening = 19.1 pp, **rating diff = 61.2 pp**. Color isn't even in the top three.

---

## 4 · Chart-by-chart explanation

Every chart pulls from a pre-aggregated JSON in `viz/data_color/`. The browser never loads the raw 4.4 GB CSV.

### Side A — Color is Destiny

#### A1 · The headline (horizontal bar)

- **Source.** `A1_headline.json` · fields `outcome`, `games`, `pct`.
- **What it shows.** Win/draw/loss across all 1.8M games as three horizontal bars.
- **Technique.** Animated horizontal bar chart. Bars grow from 0 with staggered timing.
- **Why this technique.** Position-on-common-axis is the most accurate visual encoding (Cleveland & McGill); the audience can directly compare White's 50.4% to Black's 46.5%.
- **Interactivity.** Hover any bar → tooltip with exact percentage and game count.
- **Argument.** "Look at the bars. White is longer. The advantage is real."

#### A2 · Edge across Elo (multi-line)

- **Source.** `A2_elo.json` — three rows for Elo 1000 / 1200 / 1400.
- **What it shows.** Three lines (White%, Draw%, Black%) across the three Elo bands in our filter.
- **Technique.** Multi-line chart with stroke-dasharray reveal animation.
- **Why this technique.** Lines visually convey trajectory — does the advantage shrink, grow, or stay flat as players improve?
- **Interactivity.** Hover any data point → tooltip with band, value, and game count.
- **Argument.** "The gap doesn't close as players improve — it actually widens slightly (2.5pp → 3.9pp). Skill *amplifies* the first-move advantage, not the other way around."

#### A3 · Edge across time controls (stacked bar)

- **Source.** `A3_tc.json` — bullet, blitz, rapid, classical buckets.
- **What it shows.** Stacked 100% bars showing W/D/B share per time control.
- **Technique.** Stacked bar chart with sequential animation (stack grows bottom-up).
- **Why this technique.** A part-of-whole visualisation answers "is the gap robust to changing the clock?" with one glance.
- **Interactivity.** Hover any segment → tooltip. **Click any column → smooth-scrolls to A6 and flashes the matching tug-of-war row** (cross-chart link, rubric extra credit).
- **Argument.** "Whether it's bullet, blitz, rapid, or classical, the white slice is bigger. You can't escape the gap by changing the time control."

#### A4 · White's strongest weapons (treemap)

- **Source.** `A4_white_weapons.json` — top 16 opening families with ≥2k games, ranked by White win %.
- **What it shows.** Tile area = number of games, tile brightness = White win %.
- **Technique.** Treemap (custom area-encoded grid).
- **Why this technique.** A treemap simultaneously answers "how popular is this opening?" and "how strongly does it favour White?" — two channels in one mark.
- **Interactivity.** Hover any tile → tooltip with opening family, White win %, and exact game count.
- **Argument.** "Bishop's Opening 54.4%. Italian Game 54.1%. Philidor 53.3%. White's edge isn't an artifact — it lives in concrete openings every chess teacher recommends."

#### A5 · Where White checkmates Black (heatmap)

- **Source.** `A5_mate_heatmap.json` — top 10 opening families × 3 Elo bands.
- **What it shows.** Cell colour intensity = White-mates-Black rate in each (opening, Elo) cell.
- **Technique.** Heatmap with `interpolateYlOrRd` (yellow→red) so cells remain visible against the dark page background.
- **Why this technique.** A 2D categorical-by-categorical view is a heatmap's natural use case; colour intensity carries the magnitude.
- **Interactivity.** Hover any cell → tooltip with opening, band, mate rate, and game count.
- **Argument.** "White doesn't just win — White checkmates. The heatmap glows orange-red in sharp openings (Bishop's, Italian) where mate rates exceed 25%. Black's checkmate density is half that."

#### A6 · Tug of War (innovative custom view)

- **Source.** `A6_tug_of_war.json` — 13 different cuts of the data (overall, four time controls, three Elo bands, five opening families).
- **What it shows.** Each row is a horizontal "rope" anchored at zero. The "knot" position = White's edge in percentage points; positive (right of zero) = White pulls, negative (left) = Black pulls.
- **Technique.** Custom-designed visualisation. Marks: rope (line), knot (circle). Channels: knot horizontal position (edge magnitude), knot colour (direction), rope segment colour (which side is pulling).
- **Why this technique.** This is the project's central rhetorical move. The metaphor — every cut of the data tugging on a rope — visually answers "is this advantage *everywhere*?" in a way no standard chart can.
- **Interactivity.** **Filter pills** (All / Time Control / Elo / Opening) re-render the chart with that subset of rows. Hover any knot → tooltip with the cut's exact edge and game count.
- **Argument.** "Every rope pulls toward White. The knot never crosses zero. From bullet to classical, from Elo 1000 to 1400, from the Italian Game to the Scandinavian Defense — the result is the same direction."
- **Why it's innovative.** Custom marks/channels written from scratch in D3 (no built-in `d3.tug()`); the rope-and-knot metaphor is not a standard charting convention; the filter pills produce a re-rendered re-animated diagram.

### Side B — Color is Irrelevant

#### B1 · Out of 100 games (waffle / unit chart, innovative)

- **Source.** `B1_color_share.json` — single record with `color_decided_pct` derived from the +3.9 pp gap.
- **What it shows.** A 10×10 grid of squares. The first ~4 squares are blue (color decided this game). The remaining ~96 are dark (decided by something else).
- **Technique.** Waffle / unit chart with sequential animation (squares fade in one by one).
- **Why this technique.** A unit chart converts an abstract percentage (3.9%) into a concrete tally (4 of 100 games). Reframes the audience's perception of "size" of the effect.
- **Interactivity.** Hover any square → tooltip with the framing.
- **Argument.** "Color decides four games. *Something else* decides the other 96. Whatever that something else is, it dwarfs color."

#### B2 · Black's strongest defenses (grouped horizontal bar)

- **Source.** `B2_blacks_weapons.json` — six common Black-side openings with ≥1k games.
- **What it shows.** Per-opening White win % vs Black win %, one pair of bars per opening.
- **Technique.** Grouped horizontal bar chart with paired-bar layout.
- **Why this technique.** Direct side-by-side comparison: was Black's win % bigger here? The answer is visible at a glance.
- **Interactivity.** Hover any bar → tooltip. Bars are tagged with a blue "◀" arrow when Black wins more.
- **Argument.** "The Sicilian Defense — 152,000 games, the most popular Black response in chess — is one **Black wins**. The French Defense favours Black. The Pirc favours Black. Color cannot be 'destiny' if Black's defenses systematically beat White."

#### B3 · Most extreme opening edges (diverging bar)

- **Source.** `B3_swing_extremes.json` — five most White-favouring + five most Black-favouring openings (≥500 games).
- **What it shows.** Bars diverge from a centre line. Right = Black wins more, left = White wins more.
- **Technique.** Diverging bar chart with central reference axis.
- **Why this technique.** Diverging bars make "swing magnitude" visually intuitive — the longer the bar in either direction, the more decisive that opening is.
- **Interactivity.** Hover any bar → tooltip with both percentages and the edge in pp.
- **Argument.** "Top half: openings where Black wins by 30–44 pp. Bottom half: openings where White wins by 30–80 pp. Same dataset. Same player pool. The opening choice did 20× more work than the colour did."

#### B4 · The opening spectrum (bubble scatter)

- **Source.** `B4_spectrum.json` — 60 popular openings (≥1k games each).
- **What it shows.** Each circle is one opening. X-axis = White win %, Y-axis = popularity (log scale), circle radius = game count.
- **Technique.** Bubble chart on a log Y axis with a vertical "50% fair" reference line.
- **Why this technique.** Reveals the full distribution of opening outcomes, not just the extremes. The visual spread (30%–62% on the X axis) is the rhetorical payload.
- **Interactivity.** Hover any circle → tooltip. **Click any circle → pins the opening's name as a permanent label.**
- **Argument.** "Look at how spread out the dots are. If colour were destiny, every dot would cluster near the 50% line. They don't. Some openings are 30% White; others are 62% White. The opening you played is the dot's X position. The +3.9pp from colour is a tiny shift compared to where any individual dot already sits."

#### B5 · Win rate by rating gap (stacked bar, 7 buckets)

- **Source.** `B5_rating_diff.json` — 7 buckets from "Black ≥+200" to "White ≥+200".
- **What it shows.** Stacked W/D/B per rating-gap bucket.
- **Technique.** Stacked bar chart with rotated labels for the 7 categorical buckets.
- **Why this technique.** Visually demonstrates that rating gap monotonically and dramatically swings the outcome distribution.
- **Interactivity.** Hover any segment → tooltip with bucket, side, percentage, and game count.
- **Argument.** "When Black is rated 200+ points higher, Black wins about 80%. When White is 200+ higher, White wins about 80%. Rating swings the outcome by 60 percentage points. Colour swings it by 4. Rating wins this contest 16-to-1."

#### B6 · Factor variance (innovative custom view)

- **Source.** `B6_factor_variance.json` — five predictors with their min, max, and spread of White win %.
- **What it shows.** A horizontal bar per factor. Bar length = the **spread in White win %** that factor produces when you split the dataset by it.
- **Technique.** Bar chart with semantic annotation (the colour-factor bar is tagged "← the runt") and a sort toggle (impact / alphabetical).
- **Why this technique.** This is the rhetorical climax of Side B. The chart literally measures "how much can each factor move the outcome?" and reveals that colour is the smallest. No standard "factor importance" chart exists; this is a purpose-built composite.
- **Interactivity.** **Sort toggle** between impact-magnitude and alphabetical ordering. Hover any bar → tooltip with min, max, spread, and number of subgroups.
- **Argument.** "Sort by impact. Look at the order. Rating diff (61pp) and opening choice (19pp) tower over colour (3.9pp). Colour isn't even in the top three. It's the runt."
- **Why it's innovative.** Computed metric (spread of a metric across factor levels) is non-standard; semantic annotation ("← the runt") is content-aware, not generic; sort toggle re-renders with smooth transitions; the chart is a custom answer to a question (relative impact) that no off-the-shelf chart type asks.

---

## 5 · Visual-design principles we applied

### Consistent colour encoding

| What | Encoding |
|---|---|
| White (the chess piece colour) | `#f1f1f1` — light, near-white |
| Black (the chess piece colour) | `#3b3f4c` — dark, near-charcoal |
| Draw | `#7d8597` — neutral grey |
| Side A accent | white tone (visual identity for "color matters" side) |
| Side B accent | `#5fb1ff` (a cool blue, for the "color is noise" side) |

Black-as-#3b3f4c rather than literal `#000` is a deliberate choice — pure black would disappear against the dark `#0a0d14` page background, breaking visibility for half our data. The slightly-charcoal grey reads as "Black" in a chess context while staying perceptible.

### Semantic colour use

Colour is used to communicate, not decorate. Side A's accent is white → "white wins" → confidence in the first-move advantage. Side B's accent is blue (Lichess's brand colour, conveniently also Black-suggestive) → confidence that colour-the-variable is overrated.

### Hierarchy through scale

Hero kickers use 64–96 px type. Sub-headlines use 30 px. Body copy is 15.5 px. Numbers in chart cards are 54 px to draw the eye. The hierarchy mirrors how a reader's attention should flow: hook → claim → evidence.

### Animation as narrative pacing

Charts animate in on scroll (IntersectionObserver, threshold 0.15). Inside the chart, marks animate sequentially (bars grow with stagger, lines reveal via stroke-dasharray, scatter dots appear in series). The animation is **information-bearing** — it controls when the reader processes each part of the data — not decorative.

---

## 6 · Scrollytelling design

We chose a **reveal-on-scroll** pattern over scroll-bound chart morphing (Scrollama / GSAP ScrollTrigger). Reasoning:

- The story is six discrete "beats" per side, each with its own chart. A reader who scrolls fast should still see all six. Scroll-bound morphing rewards slow readers and punishes skimmers.
- Each beat is autonomous (narrative + chart), so a reader can leave at any point with a complete sub-argument. There is no "you must read top-to-bottom" tax.
- Sticky top navigation + smooth-scroll between beats give the reader explicit control over pacing.

The narrative copy is **integrated into the page**, not held back as a separate report. Every chart card has a 380-px narrative panel to its left explaining the data point in plain language with bolded numbers. The stories are designed to be read like a piece of journalism — you should not need this PROJECT.md to understand them.

---

## 7 · Cross-chart linkage (extra-credit attempt)

The rubric awards extra credit for stories that link visualisations creatively. We implemented one such linkage:

**A3 → A6.** Click any time-control column on the A3 stacked bar chart. The page smooth-scrolls to A6's tug-of-war and flashes the matching row (Bullet / Blitz / Rapid / Classical) as a translucent overlay. This is a real DOM-level cross-chart action: it reuses A3 as a control panel for A6 without duplicating data.

We considered a global "Time Control" filter that retargets multiple charts but chose the lighter linkage to keep the scrollytelling pacing intact.

---

## 8 · Technical implementation

### Pipeline architecture

```
Lichess CSV (4.4 GB)
    ↓ DuckDB streaming read (no full RAM load)
filtered to Elo 1000–1599
    ↓ aggregations
13 small JSONs (≈200 KB total)
    ↓ d3.json() at page load
12 charts in browser
```

### Why DuckDB (and not pandas)

- Streams 6.25M rows from CSV in ~7 seconds.
- SQL aggregations are 5–10× more readable than the pandas equivalents.
- Zero install pain — `pip install duckdb` is one line, no system dependencies.

### Why we pre-aggregate to JSON instead of letting D3 compute

- The browser cannot fetch 4.4 GB.
- Aggregations are deterministic and small (max chart payload < 30 KB), so caching them server-side keeps the page reload time under 100 ms.
- The pipeline is a one-shot — re-run it only when changing the Elo filter or month.

### Why D3 v7 (and no scrolly library)

- The rubric requires D3 (NVD3, Vega-Lite, Highcharts forbidden).
- Vanilla `IntersectionObserver` for reveal is 12 lines of code; pulling Scrollama (`npm install`) for the same outcome adds dependency overhead with no rubric-relevant gain.
- D3 v7 was chosen over D3 v6 for the cleaner promise-based JSON loading.

---

## 9 · Rubric mapping

| Rubric requirement | Where it lives in the project | Status |
|---|---|---|
| Genuinely controversial topic | Chess first-mover advantage debate; both sides have real proponents | ✅ |
| Two contrasting scrollytelling stories | `side_a.html` argues edge is real; `side_b.html` argues it's noise | ✅ |
| ≥6 visualisations per side (12 total) | A1–A6 + B1–B6 | ✅ |
| ≥6 distinct visualisation techniques | bar, stacked bar, line, treemap, heatmap, scatter, waffle, diverging bar, custom tug-of-war = 9 | ✅ exceeds |
| ≥2 innovative views | A6 Tug-of-War + B6 Factor variance (3rd candidate: B1 waffle) | ✅ |
| D3.js implementation | `<script src="d3.v7.min.js">`; no banned libraries | ✅ |
| Landing page with title + team + intro + links | `index.html` with all required elements | ✅ |
| ≥25% animated/interactive (≥3 of 12) | All 12 charts have entrance animation + hover; A6 has filter pills, B4 has click-pin, B6 has sort toggle, A3 has cross-chart click | ✅ vastly exceeds |
| Scrollytelling format with vertical scroll | IntersectionObserver reveal pattern; 6 beats per side | ✅ |
| Self-explanatory narration | Every beat has narrative panel + chart card; report not required for comprehension | ✅ |
| Linked charts (extra credit) | A3 → A6 click-jump with row highlight | ✅ |
| Consistent colour scheme & sizing | Two-side palette enforced across all 12 charts; same chart-card width and padding | ✅ |
| No banned libraries (Bootstrap allowed; NVD3/Vega/Highcharts not) | None used | ✅ |
| Single index.html as project entry | Yes, root of `viz/` | ✅ |
| Avoid AI / COVID / video games / GOAT topic bans | Topic is chess strategy — not banned | ✅ |

---

## 10 · Limitations and honest caveats

- **Single-month, single-site dataset.** Lichess June 2016 is a thick slice but it is one slice. A different month, a different site (chess.com), or FIDE classical games could shift the magnitudes. The conclusions about *direction* (White edge exists; opening choice swings more) are robust; the magnitudes are slice-dependent.
- **Elo 1000–1599 only.** Above master level (Elo 2400+), the gap may close — our sample at that band is too thin to claim either way. We document the filter on every page.
- **Mate detection is regex on PGN.** We mark a game as a checkmate if its algebraic notation contains `#`. PGNs that omit the `#` notation will be undercounted — this is a known limitation of the source data.
- **Move-count is a proxy.** We approximate ply count by counting `\d+\.` move-number tokens in the AN string. This overcounts on games ending mid-move-pair. The narrative does not depend on this number.
- **Causal claims are avoided.** We never claim "playing the Sicilian *causes* Black to win." We claim "Black wins more of the games where the Sicilian was played." Correlation, not causation, throughout.

These limitations are stated to make the work honest — they do not undermine the dueling-narrative thesis, which is about the existence and relative magnitude of effects, not their underlying causes.

---

## 11 · Team and contributions

| Member | Email | Primary contribution |
|---|---|---|
| Mathew Abraham Palliambil | mpalliam@asu.edu | Heatmap (A5) and treemap (A2) design and chart-data pipeline |
| Basil Shibu Thomas | bthoma70@asu.edu | Multi-line (A2) and scatter (A6 prototype) implementations |
| Asmit Datta | adatta18@asu.edu | Headline bar (A1) and donut (A3) cards; data pre-processing pipeline lead |
| Chandana Priya Srinivasa | csrini10@asu.edu | Sankey/box-plot prototypes; Side B waffle (B1) layout |
| Kruthika Kadurhalli Raghu | kkadurha@asu.edu | Stacked bars (B3), radar (B4 prototype), narrative copy review |
| Parth Jain | pjain121@asu.edu | Diverging bar (B3) and waffle (B6) layouts; final QA against rubric |

(Six members, three nominal owners per side, as required.)

---

## 12 · Summary

We picked a topic with two genuinely defensible sides (chess's first-mover advantage), filtered a 6.25M-row dataset to its representative middle (1.8M club-level games), and built two scrollytelling D3 essays that argue the same data into opposite conclusions. Side A says the gap is real and inescapable. Side B says the gap is real but *small* — dwarfed by opening choice and rating gap. Both are true. The project leaves the verdict to the reader, which is the honest answer the data supports.

The final deliverables — `index.html`, `side_a.html`, `side_b.html`, the `data_color/` JSONs, the `preprocess_color.py` pipeline, this report — together satisfy every rubric requirement we could verify, exceed the interactivity floor by 4×, exceed the visualisation-technique floor by 50%, and include two custom-marks innovative views plus an extra-credit cross-chart link.

We hope you enjoy reading both sides as much as we enjoyed not having to pick one.
