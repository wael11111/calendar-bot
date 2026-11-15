import discord
from discord import app_commands
from discord.ext import commands

from events.event_data import EventData
from events.event_manager import event_manager
from events.event_view import EventView
from events.permissions import (
    charger_roles_autorises,
    est_administrateur,
    possede_role_autorise,
)

class Event(app_commands.Group):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(name="event", description="Créer et gérer des événements")
        self.bot = bot

    def peut_gerer_evenement(
        self,
        interaction: discord.Interaction,
        event: EventData,
    ) -> bool:
        """Vérifie si l'utilisateur peut gérer cet événement."""
        est_organisateur = interaction.user.id == event.organisateur_id
        est_admin = est_administrateur(interaction)
        est_role_autorise = possede_role_autorise(interaction)

        return est_organisateur or est_admin or est_role_autorise

    async def update_event_message(self, event: EventData) -> bool:
        """Met à jour le message Discord associé à l'événement, si possible."""
        if event.channel_id is None or event.message_id is None:
            return False

        try:
            channel = self.bot.get_channel(event.channel_id)
            if channel is None:
                channel = await self.bot.fetch_channel(event.channel_id)
            message = await channel.fetch_message(event.message_id)
            await message.edit(embed=event.to_embed(), view=EventView(event))
            return True
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return False

    @app_commands.command(name="creer", description="Créer un nouvel événement")
    @app_commands.describe(
        lieu="Lieu de l'événement",
        date="Date de l'événement (ex. : 25/12/2026)",
        heure="Heure de l'événement (ex. : 18h30)",
    )
    async def creer(
        self,
        interaction: discord.Interaction,
        lieu: str,
        date: str,
        heure: str,
    ) -> None:
        event = event_manager.create(
            lieu=lieu,
            date=date,
            heure=heure,
            organisateur_id=interaction.user.id,
        )
        view = EventView(event)
        await interaction.response.send_message(embed=event.to_embed(), view=view)

        message = await interaction.original_response()
        event.channel_id = message.channel.id
        event.message_id = message.id

    @app_commands.command(name="liste", description="Afficher les événements enregistrés")
    async def liste(self, interaction: discord.Interaction) -> None:
        if not event_manager.events:
            await interaction.response.send_message(
                "Aucun événement n'est actuellement enregistré.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="📅 Événements à venir",
            color=discord.Color.blurple(),
        )
        for event in sorted(event_manager.events.values(), key=lambda item: item.id)[:25]:
            embed.add_field(
                name=f"#{event.id} — {event.lieu}",
                value=(
                    f"**Date :** {event.date}\n"
                    f"**Heure :** {event.heure}\n"
                    f"**Participants :** {len(event.participants)}\n"
                    f"**Organisateur :** <@{event.organisateur_id}>"
                ),
                inline=False,
            )

        if len(event_manager.events) > 25:
            embed.set_footer(text="Seuls les 25 premiers événements sont affichés.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(
        name="roles",
        description="Afficher les rôles autorisés à gérer les événements",
    )
    async def roles(self, interaction: discord.Interaction) -> None:
        """Affiche les rôles autorisés à gérer les événements."""

        # Seuls les administrateurs et les rôles autorisés
        # peuvent consulter cette commande.
        if not (
            est_administrateur(interaction)
            or possede_role_autorise(interaction)
        ):
            await interaction.response.send_message(
                "Tu dois être administrateur ou posséder un rôle autorisé "
                "pour consulter cette liste.",
                ephemeral=True,
            )
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                "Cette commande doit être utilisée sur un serveur Discord.",
                ephemeral=True,
            )
            return

        roles_autorises = charger_roles_autorises()

        embed = discord.Embed(
            title="🛡️ Rôles autorisés à gérer les événements",
            description=(
                "Les membres possédant l'un des rôles ci-dessous "
                "peuvent modifier et supprimer tous les événements.\n\n"
                "La permission **Administrateur Discord** donne "
                "également ces droits."
            ),
            color=discord.Color.blurple(),
        )

        # Permission native Discord.
        embed.add_field(
            name="Administrateurs Discord",
            value="Tous les membres possédant la permission Administrateur.",
            inline=False,
        )

        # Rôles définis dans le fichier de configuration.
        if roles_autorises:
            lignes_roles = []

            for role_id in sorted(roles_autorises):
                role = interaction.guild.get_role(role_id)

                if role is not None:
                    lignes_roles.append(
                        f"• **{role.name}** (`{role.id}`)"
                    )
                else:
                    lignes_roles.append(
                        f"• ⚠️ Rôle introuvable (`{role_id}`)"
                    )

            valeur_roles = "\n".join(lignes_roles)
        else:
            valeur_roles = "Aucun rôle supplémentaire n'est configuré."

        embed.add_field(
            name="Rôles configurés",
            value=valeur_roles,
            inline=False,
        )

        embed.set_footer(
            text="Les organisateurs peuvent toujours gérer leurs propres événements."
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(name="modifier", description="Modifier un événement existant")
    @app_commands.describe(
        event_id="Identifiant de l'événement à modifier",
        lieu="Nouveau lieu (facultatif)",
        date="Nouvelle date (facultatif)",
        heure="Nouvelle heure (facultatif)",
    )
    async def modifier(
        self,
        interaction: discord.Interaction,
        event_id: int,
        lieu: str | None = None,
        date: str | None = None,
        heure: str | None = None,
    ) -> None:
        event = event_manager.get(event_id)
        if event is None:
            await interaction.response.send_message(
                f"Aucun événement ne porte l'identifiant #{event_id}.",
                ephemeral=True,
            )
            return

        if not self.peut_gerer_evenement(interaction, event):
            await interaction.response.send_message(
                "Tu dois être l'organisateur de cet événement ou un administrateur du serveur pour le modifier.",
                ephemeral=True,
            )
            return

        if lieu is None and date is None and heure is None:
            await interaction.response.send_message(
                "Indique au moins une information à modifier : lieu, date ou heure.",
                ephemeral=True,
            )
            return

        if lieu is not None:
            event.lieu = lieu
        if date is not None:
            event.date = date
        if heure is not None:
            event.heure = heure

        updated = await self.update_event_message(event)
        confirmation = f"L'événement **#{event.id}** a bien été modifié."
        if not updated:
            confirmation += (
                " Les données ont été modifiées en mémoire, mais je n'ai pas pu "
                "mettre à jour le message Discord associé."
            )
        await interaction.response.send_message(confirmation, ephemeral=True)

    @app_commands.command(name="supprimer", description="Supprimer un événement")
    @app_commands.describe(event_id="Identifiant de l'événement à supprimer")
    async def supprimer(self, interaction: discord.Interaction, event_id: int) -> None:
        event = event_manager.get(event_id)
        if event is None:
            await interaction.response.send_message(
                f"Aucun événement ne porte l'identifiant #{event_id}.",
                ephemeral=True,
            )
            return

        if not self.peut_gerer_evenement(interaction, event):
            await interaction.response.send_message(
                "Tu dois être l'organisateur de cet événement ou un administrateur du serveur pour le supprimer.",
                ephemeral=True,
            )
            return

        # On retire les boutons du message d'origine avant de supprimer les données.
        if event.channel_id is not None and event.message_id is not None:
            try:
                channel = self.bot.get_channel(event.channel_id)
                if channel is None:
                    channel = await self.bot.fetch_channel(event.channel_id)
                message = await channel.fetch_message(event.message_id)
                await message.edit(
                    content="Cet événement a été supprimé.",
                    embed=None,
                    view=None,
                )
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass

        event_manager.delete(event_id)
        await interaction.response.send_message(
            f"L'événement **#{event_id}** a été supprimé.",
            ephemeral=True,
        )
