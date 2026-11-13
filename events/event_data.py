from datetime import datetime

import discord


class EventData:
    """Contient les informations d'un événement Discord."""

    def __init__(
        self,
        event_id: int,
        lieu: str,
        date: str,
        heure: str,
        organisateur_id: int,
    ) -> None:
        self.id = event_id
        self.lieu = lieu
        self.date = date
        self.heure = heure
        self.organisateur_id = organisateur_id
        self.participants: list[int] = []
        self.channel_id: int | None = None
        self.message_id: int | None = None

    def to_embed(self) -> discord.Embed:
        participants_text = (
            "\n".join(f"• <@{user_id}>" for user_id in self.participants)
            if self.participants
            else "Aucun participant pour le moment."
        )

        embed = discord.Embed(
            title=f"🎉 Événement #{self.id} - {self.lieu}",
            description="Retrouvons-nous pour cet événement !",
            color=discord.Color.blurple(),
            timestamp=datetime.now().astimezone(),
        )
        embed.add_field(name="Lieu", value=self.lieu, inline=True)
        embed.add_field(name="Date", value=self.date, inline=True)
        embed.add_field(name="Heure", value=self.heure, inline=True)
        embed.add_field(
            name="Organisateur",
            value=f"<@{self.organisateur_id}>",
            inline=False,
        )
        embed.add_field(
            name=f"Participants ({len(self.participants)})",
            value=participants_text,
            inline=False,
        )
        return embed
