import time
import requests

# Central Limit Order Book API
CLOB = "https://clob.polymarket.com"

# Data API
DATA = "https://data-api.polymarket.com"
HEADERS = {"User-Agent": "polymarket-scraper/1.0"}


# Get list of markets (active questions)
resp = requests.get("https://clob.polymarket.com/markets?limit=2")
markets = resp.json()
print(markets["data"][0])