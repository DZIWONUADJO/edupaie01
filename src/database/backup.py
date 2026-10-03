"""Création et restauration sûres de fichiers de sauvegarde SQLite."""

import os
import sqlite3
from datetime import datetime

from src.database import connection as database_connection


def create_backup(destination_path):
    """Copie la base active vers ``destination_path`` avec l'API SQLite dédiée."""
    destination_path = os.path.abspath(destination_path)
    database_path = os.path.abspath(database_connection.DB_PATH)
    if destination_path == database_path:
        raise ValueError("La sauvegarde doit être différente de la base active.")

    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    source = sqlite3.connect(database_path)
    destination = sqlite3.connect(destination_path)
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()
    return destination_path


def restore_backup(backup_path):
    """Valide une sauvegarde, crée une copie de sécurité puis restaure la base.

    Le fichier est vérifié avant de remplacer les données actives. La copie de
    sécurité permet de revenir à l'état précédent si une restauration pose problème.
    """
    backup_path = os.path.abspath(backup_path)
    database_path = os.path.abspath(database_connection.DB_PATH)
    if backup_path == database_path:
        raise ValueError("Sélectionnez un fichier de sauvegarde différent de la base active.")

    source = sqlite3.connect(backup_path)
    try:
        integrity = source.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError("Le fichier de sauvegarde est endommagé.")

        tables = {
            row[0]
            for row in source.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        if not {"eleves", "paiements"}.issubset(tables):
            raise ValueError("Ce fichier ne contient pas le schéma EduPaie attendu.")

        required_columns = {
            "eleves": {"id", "matricule", "nom", "prenom", "classe", "frais_scolarite"},
            "paiements": {"id", "eleve_id", "montant", "date_paiement", "mode_paiement"},
        }
        for table, expected in required_columns.items():
            columns = {row[1] for row in source.execute(f"PRAGMA table_info({table})")}
            if not expected.issubset(columns):
                raise ValueError("Le schéma de la sauvegarde est incompatible avec EduPaie.")

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safety_path = os.path.join(
            os.path.dirname(database_path),
            f"edupaie_avant_restauration_{timestamp}.db",
        )
        create_backup(safety_path)

        destination = sqlite3.connect(database_path)
        try:
            source.backup(destination)
        finally:
            destination.close()
    finally:
        source.close()

    return safety_path
