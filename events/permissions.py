from pathlib import Path

import discord


# Chemin vers le fichier de configuration des rôles.
FICHIER_ROLES = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "roles_autorises.txt"
)


def charger_roles_autorises() -> set[int]:
    """Charge les identifiants des rôles autorisés depuis le fichier."""
    roles_autorises = set()

    try:
        with FICHIER_ROLES.open("r", encoding="utf-8") as fichier:
            for numero_ligne, ligne in enumerate(fichier, start=1):
                # Ignore les commentaires et les lignes vides.
                identifiant = ligne.split("#", 1)[0].strip()

                if not identifiant:
                    continue

                try:
                    roles_autorises.add(int(identifiant))
                except ValueError:
                    print(
                        f"[Permissions] Identifiant invalide "
                        f"à la ligne {numero_ligne} : {identifiant}"
                    )

    except OSError as erreur:
        print(f"[Permissions] Impossible de lire le fichier : {erreur}")

    return roles_autorises


def est_administrateur(interaction: discord.Interaction) -> bool:
    """Vérifie si l'utilisateur possède la permission Administrateur."""
    return (
        isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    )


def possede_role_autorise(interaction: discord.Interaction) -> bool:
    """Vérifie si l'utilisateur possède un rôle autorisé."""
    if not isinstance(interaction.user, discord.Member):
        return False

    roles_autorises = charger_roles_autorises()

    return any(
        role.id in roles_autorises
        for role in interaction.user.roles
    )