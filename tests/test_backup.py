"""Vérifie la copie, la restauration et le rejet des sauvegardes invalides."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.database import connection as database_connection
from src.database.backup import create_backup, restore_backup
from src.database.connection import init_db
from src.database.eleve_dao import EleveDAO


class BackupTestCase(unittest.TestCase):
    """Chaque test utilise sa propre base temporaire pour isoler ses données."""

    def setUp(self):
        """Prépare une petite base avec un élève de référence."""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = database_connection.DB_PATH
        database_connection.DB_PATH = str(Path(self.temp_directory.name) / "edupaie.db")
        init_db()
        EleveDAO.create("E001", "Alpha", "Test", "6e", 100000)

    def tearDown(self):
        """Restaure le chemin SQLite original et supprime les fichiers temporaires."""
        database_connection.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_backup_then_restore_creates_safety_copy(self):
        """La restauration retrouve les anciennes données et garde une copie avant restauration."""
        backup_path = Path(self.temp_directory.name) / "sauvegarde.db"
        create_backup(backup_path)
        EleveDAO.create("E002", "Beta", "Test", "5e", 90000)

        safety_copy = restore_backup(backup_path)

        self.assertTrue(Path(safety_copy).is_file())
        self.assertEqual([student[1] for student in EleveDAO.get_all()], ["E001"])
        database = sqlite3.connect(database_connection.DB_PATH)
        try:
            self.assertEqual(database.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        finally:
            database.close()

    def test_invalid_backup_is_rejected_without_changing_database(self):
        """Un fichier qui n'est pas une base SQLite ne doit pas remplacer les données."""
        invalid_path = Path(self.temp_directory.name) / "not-a-database.db"
        invalid_path.write_text("not a SQLite database", encoding="utf-8")

        with self.assertRaises(sqlite3.DatabaseError):
            restore_backup(invalid_path)

        self.assertEqual([student[1] for student in EleveDAO.get_all()], ["E001"])


if __name__ == "__main__":
    unittest.main()
