import discord

from events.event_data import EventData


class EventView(discord.ui.View):
    def __init__(self, event: EventData) -> None:
        # La vue reste active pendant que le processus du bot fonctionne.
        # Les événements ne sont pas encore restaurés après un redémarrage.
        super().__init__(timeout=None)
        self.event = event

    async def refresh(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(
            embed=self.event.to_embed(),
            view=self,
        )

    @discord.ui.button(
        label="Participer",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="event:join",
    )
    async def participer(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        user_id = interaction.user.id
        if user_id in self.event.participants:
            await interaction.response.send_message(
                "Tu participes déjà à cet événement !",
                ephemeral=True,
            )
            return

        self.event.participants.append(user_id)
        await self.refresh(interaction)

    @discord.ui.button(
        label="Se retirer",
        style=discord.ButtonStyle.danger,
        emoji="➖",
        custom_id="event:leave",
    )
    async def se_retirer(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        user_id = interaction.user.id
        if user_id not in self.event.participants:
            await interaction.response.send_message(
                "Tu ne participes pas à cet événement.",
                ephemeral=True,
            )
            return

        self.event.participants.remove(user_id)
        await self.refresh(interaction)
