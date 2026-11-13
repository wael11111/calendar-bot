import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

events = {}

# ===== Gestion des données =====

class EventData:

    compteur_id = 1

    def __init__(
        self,
        lieu: str,
        date: str,
        heure: str,
        organisateur: discord.Member
    ):
        self.lieu = lieu
        self.date = date
        self.heure = heure
        self.organisateur = organisateur
        self.id = EventData.compteur_id

        EventData.compteur_id += 1

        self.participants = []

    def to_embed(self):

        embed = discord.Embed(
            title=f"🎉 Événement #{self.id} - {self.lieu}",
            description="phrase à changer plus tard avec variable description",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📍 Lieu",
            value=self.lieu,
            inline=False
        )

        embed.add_field(
            name="📅 Date",
            value=f"{self.date} à {self.heure}",
            inline=False
        )

        embed.add_field(
            name="👤 Organisateur",
            value=self.organisateur.mention,
            inline=False
        )

        if self.participants:
            texte_participants = "\n".join(
                f"• {participant.mention}"
                for participant in self.participants
            )
        else:
            texte_participants = "Aucun participant"

        embed.add_field(
            name=f"👥 Participants ({len(self.participants)})",
            value=texte_participants,
            inline=False
        )

        return embed


# ===== Vues Discord =====



class EventView(discord.ui.View):

    def __init__(self, event: EventData):
        super().__init__()

        self.event = event


    @discord.ui.button(
        label="✅ Participer",
        style=discord.ButtonStyle.green
    )
    async def participer(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user not in self.event.participants:
            self.event.participants.append(interaction.user)
            await self.mettre_a_jour(interaction)
        else:
            await interaction.response.send_message(
                "Tu participes déjà !",
                ephemeral=True
            )

    @discord.ui.button(
        label="❌ Se retirer",
        style=discord.ButtonStyle.red
    )
    async def retirer(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user in self.event.participants:
            self.event.participants.remove(interaction.user)
            await self.mettre_a_jour(interaction)
        else:
            await interaction.response.send_message(
                "Tu ne participes déjà plus !",
                ephemeral=True
            )


    async def mettre_a_jour(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer()

        embed = self.event.to_embed()

        await interaction.message.edit(
            embed=embed,
            view=self
        )

# ===== Groupes de commandes =====



class Event(app_commands.Group):

    def __init__(self):
        super().__init__(
            name="event",
            description="Gestion des événements"
        )


    @app_commands.command(
        name="creer",
        description="Créer un événement"
    )
    async def creer(
        self,
        interaction: discord.Interaction,
        lieu: str,
        date: str,
        heure: str
    ):
        event = EventData(
            lieu,
            date,
            heure,
            interaction.user
        )

        events[event.id] = event

        view = EventView(event)

        embed = event.to_embed()

        await interaction.response.send_message(
            embed=embed,
            view=view
        )

    @app_commands.command(
        name="liste",
        description="Affiche tous les événements"
    )
    async def liste(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="📅 Liste des événements",
            color=discord.Color.blurple()
        )

        if not events:

            embed.description = "❌ Aucun événement."

        else:

            for event in events.values():

                embed.add_field(
                    name=f"#{event.id} • {event.lieu}",
                    value=f"{event.date} à {event.heure}\n"
                          f"Participants : {len(event.participants)}",
                    inline=False
                )

        await interaction.response.send_message(
            embed=embed
        )

    @app_commands.command(
        name="supprimer",
        description="Supprime un événement"
    )
    async def supprimer(
        self,
        interaction: discord.Interaction,
        id: int
    ):

        if id not in events:
            await interaction.response.send_message(
                "❌ Aucun événement avec cet identifiant.",
                ephemeral=True
            )
            return

        event = events[id]

        del events[id]

        await interaction.response.send_message(
            f"✅ L'événement **{event.lieu}** a été supprimé."
        )

# ===== Commandes slash =====



@bot.tree.command(
    name="ping",
    description="Répond Pong!"
)
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.tree.command(
    name="choix",
    description="Choisit un mot dans une liste."
)
async def slash_choix(
    interaction: discord.Interaction,
    mots: str,
    numero: int
):
    liste_mots = mots.split()

    if not (1 <= numero <= len(liste_mots)):
        await interaction.response.send_message(
            "Le nombre est hors limites."
        )
        return

    await interaction.response.send_message(
        liste_mots[numero-1]
    )



# ===== Commandes simples =====



@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def hello(ctx):
    await ctx.send("Salut ! Je suis vivant 👋")

@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)



# ===== Embeds =====



@bot.command()
async def embed(ctx):
    embed = discord.Embed(
        title="Mon premier embed",
        description="Créé avec discord.py",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Statut",
        value="Le bot fonctionne !",
        inline=False
    )

    await ctx.send(embed=embed)



# ===== Utilisateurs =====



@bot.command()
async def userinfo(ctx):
    user = ctx.author

    await ctx.send(
        f"Tu es {user.name} et ton ID est {user.id}"
    )



# ===== Exercices =====



@bot.command()
async def calcule(ctx, *, expression):
    try:
        resultat = eval(expression)
        await ctx.send(f"Résultat : {resultat}")
    except Exception:
        await ctx.send("Expression invalide.")

@bot.command()
async def choix(ctx, *, texte):
    parties = texte.split(";")

    if len(parties) != 2:
        await ctx.send("Format invalide.")
        return
    
    mots = parties[0].strip().split()

    try :
        nombre = int(parties[1].strip()) - 1
    except ValueError :
        await ctx.send("Le nombre est invalide.")
        return

    if not (0 <= nombre < len(mots)):
        await ctx.send("Le nombre est hors limites.")
        return

    await ctx.send(mots[nombre])



# ===== Evénements =====



@bot.event
async def on_ready():
        await bot.tree.sync()
        print(f"Connecté en tant que {bot.user}")

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Commande inconnue.")

bot.tree.add_command(Event())
bot.run(TOKEN)