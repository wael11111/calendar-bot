# Discord Event Bot

Bot Discord développé avec Python et `discord.py` pour créer et gérer des événements.

## Fonctionnalités

- `/event creer` : créer un événement avec un lieu, une date et une heure.
- `/event liste` : afficher les événements enregistrés.
- `/event modifier` : modifier le lieu, la date et/ou l'heure d'un événement.
- `/event supprimer` : supprimer un événement et désactiver les boutons de son ancien message.
- Boutons **Participer** et **Se retirer** sur le message de chaque événement.

## Prérequis

- Python 3.10 ou plus récent.
- Un bot créé dans le [Discord Developer Portal](https://discord.com/developers/applications).

## Installation

1. Cloner le dépôt ou télécharger le projet.
2. Créer et activer un environnement virtuel :

   ```bash
   python -m venv .venv
   ```

   Sous Windows PowerShell :

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

4. Copier `.env.example` sous le nom `.env`.
5. Ajouter le token du bot dans `.env`, sur la ligne `DISCORD_TOKEN=...`.
6. Démarrer le bot :

   ```bash
   python main.py
   ```

## Organisation du projet

```text
.
├── main.py
├── events/
│   ├── __init__.py
│   ├── event_data.py
│   ├── event_view.py
│   ├── event_commands.py
│   └── event_manager.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Les anciennes commandes de test peuvent être conservées dans `anciennes_commandes.py`. Ce fichier d'archive n'est pas importé par le bot.

## Limites actuelles

Les événements sont stockés en mémoire : ils sont perdus lorsque le bot s'arrête. Les boutons restent utilisables tant que le bot fonctionne, mais les vues et les événements ne sont pas encore restaurés après un redémarrage. Une prochaine étape consistera à ajouter une base de données et la restauration des vues persistantes.
