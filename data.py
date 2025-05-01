import requests
import pandas as pd


api_key = 'RGAPI-991b039c-bab5-4923-9223-155c986d07d7'
puuid = 'ENWzphwzHAOgkVkVB1m08yDbmRwBVnFXPGq5hI8Famhc7WYWR0UOxdQDWh9AaFTHRZgDvvoc0Fat-w'

headers = {"X-Riot-Token": api_key}
region = 'americas'

match_count = 500

headers = {"X-Riot-Token": api_key}

# Step 1: Get recent match IDs
match_ids_url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={match_count}"
match_ids = requests.get(match_ids_url, headers=headers).json()

# Step 2: Fetch and parse each match
match_rows = []

for match_id in match_ids:
    match_url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}"
    match_data = requests.get(match_url, headers=headers).json()

    # Extract your player’s data
    player = next(p for p in match_data['info']['participants'] if p['puuid'] == puuid)

    # Format traits
    traits = [
        f"{trait['name']}-{trait['tier_current']}"
        for trait in player['traits']
        if trait['tier_current'] > 0
    ]

    # Format units
    units = [
        f"{unit['character_id']} ({unit['tier']}★"
        for unit in player['units']
    ]

    # Build row
    row = {
        "match_id": match_id,
        "placement": player.get("placement"),
        "level": player.get("level"),
        "gold_left": player.get("gold_left"),
        "last_round": player.get("last_round"),
        "augments": player.get("augments", []),
        "traits": traits,
        "units": units
    }

    match_rows.append(row)

# Step 3: Create DataFrame and export to CSV
df = pd.DataFrame(match_rows)

# Save to file
csv_filename = "tft_match_history.csv"
df.to_csv(csv_filename, index=False)

print(f"✅ Data saved to {csv_filename}")