import discord
from discord.ext import tasks, commands
import random
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1410333688549605509

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!meow", intents=intents)

# Exemple de base (tu peux remplacer par API ou JSON)
champions = [
    {
        "name": "Ahri",
        "image": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ahri_0.jpg"
    },
    {
        "name": "Garen",
        "image": "https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Garen_0.jpg"
    }
]

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    smash_or_pass.start()

@tasks.loop(minutes=1)  # fréquence
async def smash_or_pass():
    channel = bot.get_channel(CHANNEL_ID)

    champ = random.choice(champions)

    embed = discord.Embed(
        title=f"💘 Smash or Pass — {champ['name']}",
        description="Vote avec ✅ pour SMASH ou ❌ pour PASS !",
        color=discord.Color.purple()
    )

    embed.set_image(url=champ["image"])
    embed.set_footer(text="League of Legends • Smash or Pass")

    message = await channel.send(embed=embed)

    # Réactions
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    # Thread
    await message.create_thread(
        name=f"{champ['name']} — Smash or Pass",
        auto_archive_duration=1440  # 24h
    )

bot.run(TOKEN)