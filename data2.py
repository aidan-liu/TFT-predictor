#!/usr/bin/env python3
"""
get_tft_matches_skip.py
-----------------------
• Skip the newest N matches (SKIP_FIRST)
• Pull the next M matches after that (MATCHES_NEEDED)
• Save everything to a CSV

Riot TFT-Match-v1   /matches/by-puuid/{puuid}/ids
  ├─ start  – index offset (0 = newest)   ← we use it to skip            *
  └─ count  – 1-100 IDs per call          ← hard limit from Riot docs    *
* docs: riot-watcher MatchApi.by_puuid(), developer portal :contentReference[oaicite:0]{index=0}
"""

import requests
import time
from datetime import datetime, timezone
import pandas as pd

# ─────────────── USER CONFIG ────────────────────────────────────────
API_KEY        = "RGAPI-365f2992-076e-4b01-8401-e03538d37264"   # <- replace
PUUID          = "eoX5A-HBxD7kSNOZhrNPJ2bGJs3xN2a-HrqV3KMrFG3W22PAYqjBAiRkDvC3xwCFBGHtfFOXpg-3Rw"                            # <- replace
CLUSTER        = "americas"                                     # americas|europe|asia|sea
SKIP_FIRST     = 0                                            # newest games to skip
MATCHES_NEEDED = 1_000                                          # games to download
# ────────────────────────────────────────────────────────────────────

HEADERS = {"X-Riot-Token": API_KEY}
BATCH   = 100       # Riot cap for `count`
SLEEP   = 1.2       # stay < 20 requests / second with dev key

def riot_get(url: str, **kwargs):
    """GET with helpful error messages."""
    resp = requests.get(url, headers=HEADERS, timeout=10, **kwargs)
    if resp.status_code != 200:
        try:
            err = resp.json()
        except ValueError:
            err = resp.text
        raise RuntimeError(f"Riot API {resp.status_code}: {err}")
    return resp.json()

# ─── 1.  Collect the match-IDs we want ───────────────────────────────
def collect_match_ids() -> list[str]:
    ids, start = [], SKIP_FIRST
    while len(ids) < MATCHES_NEEDED:
        left   = MATCHES_NEEDED - len(ids)
        params = {"start": start, "count": min(BATCH, left)}
        chunk  = riot_get(
            f"https://{CLUSTER}.api.riotgames.com/tft/match/v1/matches/by-puuid/{PUUID}/ids",
            params=params,
        )
        if not chunk:               # ran out of historical games
            break
        ids.extend(chunk)
        start += BATCH
        time.sleep(SLEEP)
    return ids

# ─── 2.  Fetch each match and extract our player’s row ───────────────
def fetch_matches(match_ids: list[str]) -> list[dict]:
    rows = []
    for mid in match_ids:
        try:
            m = riot_get(
                f"https://{CLUSTER}.api.riotgames.com/tft/match/v1/matches/{mid}"
            )
        except RuntimeError as err:
            print(f"⚠️  skipping {mid}: {err}")
            continue

        info   = m["info"]
        player = next(p for p in info["participants"] if p["puuid"] == PUUID)

        rows.append(
            dict(
                match_id  = mid,
                game_time = datetime.fromtimestamp(info["game_datetime"] / 1000,
                                                   tz=timezone.utc),
                placement = player["placement"],
                level     = player["level"],
                gold_left = player["gold_left"],
                augments  = player.get("augments", []),
                traits    = [
                    f"{t['name']}-{t['tier_current']}"
                    for t in player["traits"] if t["tier_current"]
                ],
                units     = [
                    f"{u['character_id']} ({u['tier']}★)"
                    for u in player["units"]
                ],
            )
        )
        time.sleep(SLEEP)
    return rows

def main() -> None:
    print(f"➡️  Skipping {SKIP_FIRST} newest matches, "
          f"collecting next {MATCHES_NEEDED} …")
    ids  = collect_match_ids()
    print(f"   • Retrieved {len(ids)} match IDs")

    rows = fetch_matches(ids)
    print(f"   • Pulled {len(rows)} full match payloads")

    if not rows:
        print("No data – nothing to save.")
        return

    df = pd.DataFrame(rows)
    out_file = (
        f"tft_{PUUID[:8]}_{len(rows)}matches_after_{SKIP_FIRST}skip.csv"
    )
    df.to_csv(out_file, index=False)
    print(f"✅  Saved {out_file}")

if __name__ == "__main__":
    main()
