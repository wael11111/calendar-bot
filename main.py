import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from events.event_commands import Event
from events.database import Database


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


class EventBot(commands.Bot):
    async def setup_hook(self) -> None:
        # Ouvre la connexion à la base de données.
        self.db = Database()
        await self.db.connect()
        print("Connexion à SQLite réussie.")

        # Enregistre les commandes slash une fois au démarrage.
        await self.tree.sync()
        print("Commandes slash synchronisées.")

    async def close(self) -> None:
        # Ferme la connexion à la base de données.
        if hasattr(self, "db"):
            await self.db.close()
            print("Connexion SQLite fermée.")

        await super().close()

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
