import discord
from discord.ext import tasks, commands
import random
import os
from dotenv import load_dotenv
from datetime import datetime
import requests


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = int(os.getenv("CHANNEL_ID"))  # Convert to integer

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!meow", intents=intents)

def get_all_champions():
    url = "https://ddragon.leagueoflegends.com/cdn/14.1.1/data/fr_FR/champion.json"
    response = requests.get(url)
    data = response.json()

    champions = []

    for champ in data["data"].values():
        name = champ["name"]
        key = champ["id"]  # ex: Ahri, Garen

        image_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{key}_0.jpg"

        champions.append({
            "name": name,
            "image": image_url
        })

    return champions

# Exemple de base (tu peux remplacer par API ou JSON)
champions = get_all_champions()

# Liste dynamique (copie)
champions_restants = champions.copy()


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    smash_or_pass.start()

@tasks.loop(minutes=1)
async def smash_or_pass():
    global champions_restants

    channel = bot.get_channel(CHANNEL)

    # 🔄 Reset si tous les champions ont été utilisés
    if not champions_restants:
        champions_restants = champions.copy()

    champ = random.choice(champions_restants)
    champions_restants.remove(champ)  # ❌ on retire le champion

    # 🕒 Date actuelle
    now = datetime.now()

    embed = discord.Embed(
        title=f"💘 Smash or Pass — {champ['name']}",
        description="Vote avec ✅ pour SMASH ou ❌ pour PASS !",
        color=discord.Color.purple(),
        timestamp=now  # ⬅️ affiche date + heure
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

bot.run(TOKEN)