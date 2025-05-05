import requests

# Replace with your Riot API key
api_key = "RGAPI-0fd506dc-663d-4e79-8009-047d2666c362"

# Riot ID input
game_name = "Riot Mortdog"     # Username (case-sensitive)
tag_line = "Mort"            # Tagline (region tag, e.g. NA1, EUW, KR, etc.)

# This endpoint uses the global routing value
url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
headers = {"X-Riot-Token": api_key}
response = requests.get(url, headers=headers)

# Check and parse
if response.status_code != 200:
    print(f"❌ Error {response.status_code}: {response.text}")
else:
    data = response.json()
    print("✅ Game Name:", data["gameName"])
    print("✅ Tag Line:", data["tagLine"])
    print("✅ PUUID:", data["puuid"])
