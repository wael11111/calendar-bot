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

    async def close(self) -> None:
        """Ferme la connexion à la base de données."""
        if self.connection is not None:
            await self.connection.close()
            self.connection = None
