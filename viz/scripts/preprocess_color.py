"""Color-narrative preprocessing pipeline.

Produces JSONs for two contrasting scrollytelling stories:
  Side A — Color is Destiny:  White's first-move advantage is real.
  Side B — Color is Irrelevant: at club level, opening choice & time control
                                 swamp whatever color you got.

Filter: Elo 1000-1599 (1.8M games). Run:
    python preprocess_color.py
"""
from __future__ import annotations
import json, time
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT.parent / "data2" / "chess_games.csv"
OUT = ROOT / "data_color"
OUT.mkdir(parents=True, exist_ok=True)
ELO_MIN, ELO_MAX = 1000, 1599


def write_json(name, payload):
    p = OUT / f"{name}.json"
    p.write_text(json.dumps(payload, indent=2, default=str))
    print(f"  wrote {p.relative_to(ROOT)}")


def main():
    con = duckdb.connect()
    print(f"[preprocess_color] elo=[{ELO_MIN},{ELO_MAX}]")
    t0 = time.time()
    con.execute(f"""
        CREATE OR REPLACE TABLE games AS
        SELECT
            ECO, Opening, Result, Termination,
            REGEXP_REPLACE(SPLIT_PART(Opening, ':', 1), ' #[0-9]+$', '') AS opening_family,
            CASE Result WHEN '1-0' THEN 'white_win'
                        WHEN '0-1' THEN 'black_win'
                        WHEN '1/2-1/2' THEN 'draw' END AS outcome,
            CAST(FLOOR(((COALESCE(WhiteElo,0)+COALESCE(BlackElo,0))/2.0)/200)*200 AS INTEGER) AS elo_band,
            WhiteElo, BlackElo,
            (WhiteElo - BlackElo) AS rating_diff,
            CASE
              WHEN TimeControl LIKE '%+%' THEN
                CASE
                  WHEN CAST(SPLIT_PART(TimeControl,'+',1) AS INTEGER) < 180  THEN 'bullet'
                  WHEN CAST(SPLIT_PART(TimeControl,'+',1) AS INTEGER) < 600  THEN 'blitz'
                  WHEN CAST(SPLIT_PART(TimeControl,'+',1) AS INTEGER) < 1800 THEN 'rapid'
                  ELSE 'classical' END
              ELSE 'unknown' END AS tc_bucket,
            (AN LIKE '%#%') AS is_mate
        FROM read_csv_auto('{CSV.as_posix()}', IGNORE_ERRORS=TRUE)
        WHERE Result IN ('1-0','0-1','1/2-1/2')
          AND Opening IS NOT NULL
          AND ((COALESCE(WhiteElo,0)+COALESCE(BlackElo,0))/2.0) BETWEEN {ELO_MIN} AND {ELO_MAX}
    """)
    n = con.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    print(f"  loaded+filtered {n:,} rows in {time.time()-t0:.1f}s")

    # ============= META =============
    overall = con.execute("""
        SELECT COUNT(*) AS n,
               100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct,
               100.0*SUM(CASE WHEN outcome='draw'      THEN 1 ELSE 0 END)/COUNT(*) AS draw_pct,
               100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS black_pct
        FROM games
    """).fetchone()
    write_json("00_meta", {
        "total_games": overall[0],
        "white_pct": round(overall[1], 2),
        "draw_pct":  round(overall[2], 2),
        "black_pct": round(overall[3], 2),
        "white_edge": round(overall[1] - overall[3], 2),
        "elo_min": ELO_MIN, "elo_max": ELO_MAX,
    })

    # ============= SIDE A — Color is DESTINY =============

    # A1. Headline bar
    rows = con.execute("""
        SELECT outcome, COUNT(*) AS games,
               100.0*COUNT(*)/SUM(COUNT(*)) OVER() AS pct
        FROM games GROUP BY outcome
        ORDER BY CASE outcome WHEN 'white_win' THEN 1 WHEN 'draw' THEN 2 ELSE 3 END
    """).df().to_dict(orient="records")
    write_json("A1_headline", rows)

    # A2. Edge across Elo (line)
    rows = con.execute("""
        SELECT elo_band, COUNT(*) AS games,
               100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct,
               100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS black_pct,
               100.0*SUM(CASE WHEN outcome='draw'      THEN 1 ELSE 0 END)/COUNT(*) AS draw_pct
        FROM games WHERE elo_band BETWEEN 1000 AND 1400
        GROUP BY elo_band HAVING games >= 1000
        ORDER BY elo_band
    """).df().to_dict(orient="records")
    write_json("A2_elo", rows)

    # A3. Edge across time controls (grouped bar)
    rows = con.execute("""
        SELECT tc_bucket, COUNT(*) AS games,
               100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct,
               100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS black_pct,
               100.0*SUM(CASE WHEN outcome='draw'      THEN 1 ELSE 0 END)/COUNT(*) AS draw_pct
        FROM games WHERE tc_bucket <> 'unknown'
        GROUP BY tc_bucket
    """).df().to_dict(orient="records")
    order = {'bullet':1,'blitz':2,'rapid':3,'classical':4}
    rows.sort(key=lambda r: order.get(r['tc_bucket'], 99))
    write_json("A3_tc", rows)

    # A4. Top White-winning openings (≥2000 games) — treemap
    rows = con.execute("""
        SELECT opening_family, COUNT(*) AS games,
               100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_win_pct
        FROM games GROUP BY opening_family
        HAVING games >= 2000
        ORDER BY white_win_pct DESC LIMIT 16
    """).df().to_dict(orient="records")
    write_json("A4_white_weapons", rows)

    # A5. White-mate heatmap (top 10 popular openings × elo)
    rows = con.execute("""
        WITH top AS (
            SELECT opening_family FROM games
            GROUP BY opening_family ORDER BY COUNT(*) DESC LIMIT 10
        )
        SELECT g.opening_family, g.elo_band, COUNT(*) AS games,
               100.0*SUM(CASE WHEN g.outcome='white_win' AND g.is_mate THEN 1 ELSE 0 END)/COUNT(*) AS white_mate_pct
        FROM games g JOIN top USING (opening_family)
        WHERE g.elo_band BETWEEN 1000 AND 1400
        GROUP BY g.opening_family, g.elo_band
        HAVING games >= 200
        ORDER BY g.opening_family, g.elo_band
    """).df().to_dict(orient="records")
    write_json("A5_mate_heatmap", rows)

    # A6 INNOVATIVE. "Tug-of-War" data — simulating subgroups
    # For each cut, compute white_edge so we can render a single tug-of-war strip
    cuts = []
    for label, sql in [
        ("Overall",            "SELECT * FROM games"),
        ("Bullet",             "SELECT * FROM games WHERE tc_bucket='bullet'"),
        ("Blitz",              "SELECT * FROM games WHERE tc_bucket='blitz'"),
        ("Rapid",              "SELECT * FROM games WHERE tc_bucket='rapid'"),
        ("Classical",          "SELECT * FROM games WHERE tc_bucket='classical'"),
        ("Elo 1000",           "SELECT * FROM games WHERE elo_band=1000"),
        ("Elo 1200",           "SELECT * FROM games WHERE elo_band=1200"),
        ("Elo 1400",           "SELECT * FROM games WHERE elo_band=1400"),
        ("Italian Game",       "SELECT * FROM games WHERE opening_family='Italian Game'"),
        ("Bishop's Opening",   "SELECT * FROM games WHERE opening_family='Bishop''s Opening'"),
        ("Ruy Lopez",          "SELECT * FROM games WHERE opening_family='Ruy Lopez'"),
        ("Scandinavian",       "SELECT * FROM games WHERE opening_family='Scandinavian Defense'"),
        ("Philidor",           "SELECT * FROM games WHERE opening_family='Philidor Defense'"),
    ]:
        r = con.execute(f"""
            SELECT COUNT(*) AS n,
              100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS w,
              100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS b
            FROM ({sql}) t
        """).fetchone()
        cuts.append({"label": label, "games": r[0], "white_pct": r[1], "black_pct": r[2],
                     "edge": (r[1] or 0) - (r[2] or 0)})
    write_json("A6_tug_of_war", cuts)


    # ============= SIDE B — Color is IRRELEVANT =============

    # B1. 96-of-100 framing — same as overall but split into "color-decided" vs "other"
    # We frame it as: 50.4 (W) - 46.5 (B) = 3.9pp = 4 games of 100 are "extra White wins"
    # The OTHER 96 of 100 games' outcomes are determined by something else (not color)
    rows = con.execute("""
        SELECT COUNT(*) AS games,
               100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct,
               100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS black_pct,
               100.0*SUM(CASE WHEN outcome='draw'      THEN 1 ELSE 0 END)/COUNT(*) AS draw_pct
        FROM games
    """).df().to_dict(orient="records")[0]
    edge = rows['white_pct'] - rows['black_pct']
    write_json("B1_color_share", {
        "color_decided_pct": round(edge, 2),
        "rest_pct": round(100 - edge, 2),
        **rows,
    })

    # B2. Sicilian flip — top opening is Sicilian, Black wins
    rows = con.execute("""
        SELECT opening_family, COUNT(*) AS games,
               100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct,
               100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS black_pct
        FROM games
        WHERE opening_family IN ('Sicilian Defense','French Defense','Caro-Kann Defense','Scandinavian Defense','Pirc Defense','Modern Defense')
        GROUP BY opening_family ORDER BY games DESC
    """).df().to_dict(orient="records")
    write_json("B2_blacks_weapons", rows)

    # B3. Opening swings ±70pp — extremes
    rows = con.execute("""
        WITH cand AS (
            SELECT opening_family, COUNT(*) AS games,
                   100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct,
                   100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS black_pct
            FROM games GROUP BY opening_family HAVING games >= 500
        )
        SELECT *, (white_pct - black_pct) AS edge FROM cand
        ORDER BY edge ASC LIMIT 5
    """).df().to_dict(orient="records") + con.execute("""
        WITH cand AS (
            SELECT opening_family, COUNT(*) AS games,
                   100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct,
                   100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS black_pct
            FROM games GROUP BY opening_family HAVING games >= 500
        )
        SELECT *, (white_pct - black_pct) AS edge FROM cand
        ORDER BY edge DESC LIMIT 5
    """).df().to_dict(orient="records")
    write_json("B3_swing_extremes", rows)

    # B4. Opening spectrum — every popular opening as a dot
    rows = con.execute("""
        SELECT opening_family, COUNT(*) AS games,
               100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct,
               100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS black_pct
        FROM games GROUP BY opening_family
        HAVING games >= 1000
        ORDER BY games DESC LIMIT 60
    """).df().to_dict(orient="records")
    write_json("B4_spectrum", rows)

    # B5. Rating-diff bucket — does rating predict more than color?
    rows = con.execute("""
        SELECT
          CASE
            WHEN rating_diff <= -200 THEN 'Black ≥+200'
            WHEN rating_diff <= -100 THEN 'Black +100..200'
            WHEN rating_diff <= -25  THEN 'Black +25..100'
            WHEN rating_diff <  25   THEN 'Even (±25)'
            WHEN rating_diff <  100  THEN 'White +25..100'
            WHEN rating_diff <  200  THEN 'White +100..200'
            ELSE 'White ≥+200'
          END AS bucket,
          COUNT(*) AS games,
          100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct,
          100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) AS black_pct,
          100.0*SUM(CASE WHEN outcome='draw'      THEN 1 ELSE 0 END)/COUNT(*) AS draw_pct
        FROM games
        WHERE WhiteElo IS NOT NULL AND BlackElo IS NOT NULL
        GROUP BY bucket
    """).df().to_dict(orient="records")
    order = {'Black ≥+200':1,'Black +100..200':2,'Black +25..100':3,'Even (±25)':4,
             'White +25..100':5,'White +100..200':6,'White ≥+200':7}
    rows.sort(key=lambda r: order.get(r['bucket'], 99))
    write_json("B5_rating_diff", rows)

    # B6 INNOVATIVE. "Factor variance" — for each predictor, compute the spread of white_pct it produces
    # i.e., how much can each factor MOVE white's win rate?
    factors = []

    def spread(label, sql):
        r = con.execute(f"""
            WITH cuts AS ({sql})
            SELECT MIN(white_pct) AS lo, MAX(white_pct) AS hi, COUNT(*) AS subgroups
            FROM cuts
        """).fetchone()
        return {"factor": label, "lo": r[0], "hi": r[1], "spread": (r[1] or 0) - (r[0] or 0), "subgroups": r[2]}

    factors.append(spread("Color (W vs B baseline)",
        """SELECT 'all' AS k, 100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct FROM games
           UNION ALL SELECT 'inverse', 100.0*SUM(CASE WHEN outcome='black_win' THEN 1 ELSE 0 END)/COUNT(*) FROM games"""))
    factors.append(spread("Time control (4 buckets)",
        """SELECT tc_bucket AS k, 100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct
           FROM games WHERE tc_bucket<>'unknown' GROUP BY tc_bucket"""))
    factors.append(spread("Elo band (3 bands)",
        """SELECT elo_band AS k, 100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct
           FROM games WHERE elo_band BETWEEN 1000 AND 1400 GROUP BY elo_band HAVING COUNT(*)>=1000"""))
    factors.append(spread("Opening (top 60)",
        """SELECT opening_family AS k, 100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct
           FROM games GROUP BY opening_family HAVING COUNT(*)>=1000 ORDER BY COUNT(*) DESC LIMIT 60"""))
    factors.append(spread("Rating diff (7 buckets)",
        """SELECT
            CASE
              WHEN rating_diff <= -200 THEN 'Black ≥+200'
              WHEN rating_diff <= -100 THEN 'Black +100..200'
              WHEN rating_diff <= -25  THEN 'Black +25..100'
              WHEN rating_diff <  25   THEN 'Even (±25)'
              WHEN rating_diff <  100  THEN 'White +25..100'
              WHEN rating_diff <  200  THEN 'White +100..200'
              ELSE 'White ≥+200' END AS k,
            100.0*SUM(CASE WHEN outcome='white_win' THEN 1 ELSE 0 END)/COUNT(*) AS white_pct
            FROM games WHERE WhiteElo IS NOT NULL AND BlackElo IS NOT NULL GROUP BY k"""))
    write_json("B6_factor_variance", factors)

    print("[done]")


if __name__ == "__main__":
    main()
