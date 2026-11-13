import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from events.event_commands import Event


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


class EventBot(commands.Bot):
    async def setup_hook(self) -> None:
        # Enregistre les commandes slash une fois au démarrage.
        await self.tree.sync()
        print("Commandes slash synchronisées.")


intents = discord.Intents.default()
bot = EventBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID : {bot.user.id})")


bot.tree.add_command(Event(bot))


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(
            "Le token Discord est introuvable. Vérifie le fichier .env et la variable DISCORD_TOKEN."
        )
    bot.run(TOKEN)
