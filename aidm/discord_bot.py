import logging
import os
import threading
from pathlib import Path
from typing import Optional

import discord
from flask import Flask

from aidm import AIDungeonMaster

DEFAULT_PROMPT_PATH = Path("prompts/aidm-system-prompt.txt")
DEFAULT_SAVE_PATH = Path("history/aidm-chat-history.json")
DISCORD_TOKEN = os.environ["AI_DM_BOT_KEY"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Application Flask minimale pour satisfaire Render et garder le service éveillé
app = Flask(__name__)

@app.route("/")
def home():
    return "AI Dungeon Master Bot is alive!"

def initialize_ai_dungeon_master(
    system_prompt_path: Path = DEFAULT_PROMPT_PATH, history_path: Optional[Path] = None
) -> AIDungeonMaster:
    if history_path is not None:
        aidm = AIDungeonMaster.construct_from_history(history_path=history_path)
    else:
        aidm = AIDungeonMaster(system_prompt=system_prompt_path)
    return aidm

async def handle_message(message: discord.Message) -> None:
    # Le bot répond à tout le monde sauf à lui-même
    if message.author == client.user:
        return

    if message.content == "#save":
        aidm.save_message_history(DEFAULT_SAVE_PATH)
        await message.channel.send("Conversation history saved")
        return

    logging.info(
        f"author: {message.author}\nchannel: {message.channel}\ncontent: {message.content}\nembeds: {message.embeds}"
    )

    ai_message = aidm.query_model(message.content)
    await message.channel.send(ai_message)

@client.event
async def on_ready():
    logging.info(f"{client.user} is now running and connected to Discord!")

@client.event
async def on_message(message: discord.Message) -> None:
    logging.info(f"Message received from user: {message.author}")
    await handle_message(message)

def run_dm_bot(system_prompt_path: Path, history_path: Optional[Path] = None) -> None:
    global aidm
    aidm = initialize_ai_dungeon_master(system_prompt_path=system_prompt_path, history_path=history_path)
    
    # Lancement du bot Discord dans un thread séparé pour ne pas bloquer Flask
    discord_thread = threading.Thread(target=lambda: client.run(DISCORD_TOKEN))
    discord_thread.daemon = True
    discord_thread.start()

    # Démarrage de Flask sur le port 8080 exigé par Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
