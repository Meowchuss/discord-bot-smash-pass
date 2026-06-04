import discord
from discord.ext import tasks, commands
import random
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
import json
import os
from datetime import time


#variables globales et fonctions de gestion de l'état des champions tirés

STATE_FILE = "smash_state.json"

HORAIRES = [6, 10, 14, 18, 22]

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Convert to integer

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!meow", intents=intents)

def get_all_champions():
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
    
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/fr_FR/champion.json"
    data = requests.get(url).json()

    champions = []

    for champ in data["data"].values():
        champions.append({
            "name": champ["name"],
            "image": f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ['name']}_0.jpg"
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


def sauvegarder(champion):
    if os.path.exists(SAVE_FILE):

        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    else:
        data = {"deja_tires": []}

    if champion["name"] not in data["deja_tires"]:
        data["deja_tires"].append(champion["name"])

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

def charger():
    global champions_restants

    # Premier lancement du bot
    if not os.path.exists(SAVE_FILE):
        champions_restants = champions.copy()

        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"deja_tires": []},
                f,
                indent=4,
                ensure_ascii=False
            )

        return

    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    deja_tires = set(data.get("deja_tires", []))

    champions_restants = [
        champion
        for champion in champions
        if champion["name"] not in deja_tires
    ]

    # Tous les champions ont été utilisés
    if not champions_restants:
        champions_restants = champions.copy()

        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"deja_tires": []},
                f,
                indent=4,
                ensure_ascii=False
            )
    
async def envoyer_smash_or_pass(bot, channel):
    global champions

    state = load_state()
    today = ensure_today(state)

    # 🔄 reset champions si vide
    used = set(state["used_champions"])
    available = [c for c in champions if c["name"] not in used]

    if not available:
        state["used_champions"] = []
        available = champions.copy()

    champ = random.choice(available)

    embed = discord.Embed(
        title=f"💘 Smash or Pass — {champ['name']}",
        description=(
        "Vote avec ✅ pour SMASH ou ❌ pour PASS !\n\n"
        f"📊 Champion #{len(champions) - len(champions_restants)} / {len(champions)}"
    ),
        color=discord.Color.purple(),
        timestamp=datetime.now()  # ⬅️ affiche date + heure
    )

    embed.set_image(url=champ["image"])
    embed.set_footer(text="League of Legends • Smash or Pass")

    message = await channel.send(embed=embed)
    

    # Réactions
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    # Thread
    thread = await message.create_thread(
        name=f"{champ['name']} — Smash or Pass",
        auto_archive_duration=1440
    )
    await thread.send("Débattez ici 👇")


     # 💾 update state APRÈS succès
    state["used_champions"].append(champ["name"])
    state["days"][today][str(datetime.now().hour)] = True
    save_state(state)


# Exemple de base (tu peux remplacer par API ou JSON)
champions = get_all_champions()

# Liste dynamique (copie)
champions_restants = []
charger()



@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    await bot.load_extension("commands.verification_role")
    synced = await bot.tree.sync()
    print(f"{len(synced)} commandes synchronisées")

    if not smash_loop.is_running():
        smash_loop.start()

@tasks.loop(minutes=1)
async def smash_loop():
    now = datetime.now()
    hour = now.hour

    if hour not in HORAIRES:
        return

    state = load_state()
    today = ensure_today(state)

    # ❌ déjà envoyé ?
    if state["days"][today].get(str(hour), False):
        return

    channel = bot.get_channel(CHANNEL_ID)

    if channel:
        await envoyer_smash_or_pass(bot, channel)


bot.run(TOKEN)