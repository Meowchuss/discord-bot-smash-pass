import requests
import json
import os
from datetime import datetime



STATE_FILE = "smash_state.json"

HORAIRES = [6, 10, 14, 18, 22]

def get_all_champions():
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
    
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/fr_FR/champion.json"
    data = requests.get(url).json()

    champions = []

    for champ in data["data"].values():
        champions.append({
            "name": champ["name"],
            "image": f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ['id']}_0.jpg"
        })

    return champions

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "used_champions": [],
            "days": {}
        }

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)

def ensure_today(state):
    today = datetime.now().strftime("%Y-%m-%d")

    if today not in state["days"]:
        state["days"][today] = {
            str(h): False for h in HORAIRES
        }

    return today
