from events.event_data import EventData


class EventManager:
    def __init__(self):
        self.events: dict[int, EventData] = {}

    async def create(
        self,
        db,
        guild_id: int,
        lieu: str,
        date: str,
        heure: str,
        organisateur_id: int,
    ) -> EventData:

        # Création dans la base et récupération de l'ID.
        event_id = await db.create_event(
            guild_id=guild_id,
            organisateur_id=organisateur_id,
            lieu=lieu,
            date=date,
            heure=heure,
        )

        # Création de l'objet Python correspondant.
        event = EventData(
            event_id=event_id,
            lieu=lieu,
            date=date,
            heure=heure,
            organisateur_id=organisateur_id,
        )

        self.events[event.id] = event

        return event

    def get(self, event_id: int) -> EventData | None:
        return self.events.get(event_id)

    async def delete(self, db, event_id: int) -> EventData | None:

        # Suppression dans la base.
        await db.delete_event(event_id)

        # Suppression en mémoire.
        return self.events.pop(event_id, None)


event_manager = EventManager()