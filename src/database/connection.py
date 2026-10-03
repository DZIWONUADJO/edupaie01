"""Gestion des connexions SQLite et initialisation de la base EduPaie."""

from contextlib import contextmanager
import sqlite3
import os

# Les chemins sont calculés depuis ce fichier pour que l'application fonctionne
# même si elle est lancée depuis un autre dossier.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "edupaie.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "data", "schema.sql")

@contextmanager
def get_connection():
    """Ouvre SQLite et garantit validation, annulation ou fermeture.

    Utiliser ``with get_connection() as conn`` évite de laisser le fichier DB
    verrouillé. Une erreur annule la transaction; sinon les changements sont validés.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Crée les tables manquantes à partir du schéma SQL du projet."""
    with get_connection() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
