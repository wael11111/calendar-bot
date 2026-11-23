from pathlib import Path

import aiosqlite


# Chemin vers la base de données SQLite.
DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "events.db"
)


class Database:
    def __init__(self):
        self.connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Ouvre la connexion et initialise les tables."""
        self.connection = await aiosqlite.connect(DB_PATH)

        # Permet de récupérer les colonnes par leur nom.
        self.connection.row_factory = aiosqlite.Row

        # Active les clés étrangères pour cette connexion.
        await self.connection.execute("PRAGMA foreign_keys = ON")

        # Améliore la gestion des accès concurrents.
        await self.connection.execute("PRAGMA journal_mode = WAL")

        await self.initialize()

    async def initialize(self) -> None:
        """Crée les tables si elles n'existent pas."""

        await self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER,
                message_id INTEGER,
                organisateur_id INTEGER NOT NULL,
                lieu TEXT NOT NULL,
                date TEXT NOT NULL,
                heure TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open'
            );

            CREATE TABLE IF NOT EXISTS participants (
                event_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,

                PRIMARY KEY (event_id, user_id),

                FOREIGN KEY (event_id)
                    REFERENCES events(id)
                    ON DELETE CASCADE
            );
        """)

        await self.connection.commit()

    async def create_event(
        self,
        guild_id: int,
        organisateur_id: int,
        lieu: str,
        date: str,
        heure: str,
    ) -> int:
        """Enregistre un événement et retourne son ID."""

        cursor = await self.connection.execute(
            """
            INSERT INTO events (
                guild_id,
                organisateur_id,
                lieu,
                date,
                heure
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (guild_id, organisateur_id, lieu, date, heure),
        )

        await self.connection.commit()

        return cursor.lastrowid

    async def update_event_message(
        self,
        event_id: int,
        channel_id: int,
        message_id: int,
    ) -> None:
        """Enregistre le salon et le message Discord d'un événement."""

        await self.connection.execute(
            """
            UPDATE events
            SET channel_id = ?, message_id = ?
            WHERE id = ?
            """,
            (channel_id, message_id, event_id),
        )

        await self.connection.commit()

    async def get_events(self) -> list:
        """Récupère tous les événements enregistrés."""

        cursor = await self.connection.execute(
            "SELECT * FROM events ORDER BY id"
        )

        return await cursor.fetchall()

    async def delete_event(self, event_id: int) -> None:
        """Supprime un événement de la base."""

        await self.connection.execute(
            "DELETE FROM events WHERE id = ?",
            (event_id,),
        )

        await self.connection.commit()

    async def add_participant(
        self,
        event_id: int,
        user_id: int,
    ) -> None:
        """Ajoute un participant à un événement."""

        await self.connection.execute(
            """
            INSERT INTO participants (event_id, user_id)
            VALUES (?, ?)
            """,
            (event_id, user_id),
        )

        await self.connection.commit()

    async def remove_participant(
        self,
        event_id: int,
        user_id: int,
    ) -> None:
        """Retire un participant d'un événement."""

        await self.connection.execute(
            """
            DELETE FROM participants
            WHERE event_id = ? AND user_id = ?
            """,
            (event_id, user_id),
        )

        await self.connection.commit()

    async def get_participants(
        self,
        event_id: int,
    ) -> list[int]:
        """Récupère les IDs des participants d'un événement."""

        cursor = await self.connection.execute(
            """
            SELECT user_id
            FROM participants
            WHERE event_id = ?
            """,
            (event_id,),
        )

        rows = await cursor.fetchall()

        return [row["user_id"] for row in rows]

    async def close(self) -> None:
        """Ferme la connexion à la base de données."""
        if self.connection is not None:
            await self.connection.close()
            self.connection = None
