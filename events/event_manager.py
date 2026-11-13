from events.event_data import EventData


class EventManager:
    """Centralise les événements conservés en mémoire."""

    def __init__(self) -> None:
        self.events: dict[int, EventData] = {}
        self.next_id = 1

    def create(self, lieu: str, date: str, heure: str, organisateur_id: int) -> EventData:
        event = EventData(
            event_id=self.next_id,
            lieu=lieu,
            date=date,
            heure=heure,
            organisateur_id=organisateur_id,
        )
        self.events[event.id] = event
        self.next_id += 1
        return event

    def get(self, event_id: int) -> EventData | None:
        return self.events.get(event_id)

    def delete(self, event_id: int) -> EventData | None:
        return self.events.pop(event_id, None)


# Une seule instance partagée par les commandes et les vues.
event_manager = EventManager()
