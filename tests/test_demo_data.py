"""Vérifie que le jeu de démonstration est complet et peut être relancé sans doublons."""

import tempfile
import unittest
from pathlib import Path

import src.database.connection as database_connection
from src.database.connection import init_db
from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO
from src.database.seed_demo_data import load_demo_data
from src.services.eleve_service import EleveService


class DemoDataTestCase(unittest.TestCase):
    """Utilise une base temporaire pour ne pas charger les exemples en base réelle."""

    def setUp(self):
        """Prépare une base SQLite vide réservée à ce test."""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = database_connection.DB_PATH
        database_connection.DB_PATH = str(Path(self.temp_directory.name) / "demo.db")
        init_db()

    def tearDown(self):
        """Restaure le chemin de la base active et supprime la base temporaire."""
        database_connection.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_demo_dataset_has_expected_students_payments_and_statuses(self):
        """Le jeu contient des élèves en retard, en cours et soldés, sans doublons au rechargement."""
        self.assertEqual(load_demo_data(), (5, 6))
        self.assertEqual(load_demo_data(), (5, 6))
        self.assertEqual(len(EleveDAO.get_all()), 5)

        statuses = {student["statut"] for student in EleveService.obtenir_liste_eleves_avec_solde()}
        self.assertTrue({"En retard", "En cours", "Soldé"}.issubset(statuses))

        demo_student = next(student for student in EleveDAO.get_all() if student[1] == "DEMO-001")
        self.assertEqual(len(PaiementDAO.get_by_eleve(demo_student[0])), 2)


if __name__ == "__main__":
    unittest.main()
