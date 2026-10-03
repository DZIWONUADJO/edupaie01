"""Tests Qt du filtrage des élèves et de la sélection du menu latéral."""

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton

from src.database import connection as database_connection
from src.database.connection import init_db
from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO
from src.main_window import MainWindow


class DashboardFiltersTestCase(unittest.TestCase):
    """Utilise une fenêtre Qt et une base de données isolées des données utilisateur."""

    @classmethod
    def setUpClass(cls):
        """Démarre Qt une fois pour tous les tests de cette classe."""
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        """Crée deux élèves afin de vérifier des classes et statuts différents."""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = database_connection.DB_PATH
        database_connection.DB_PATH = str(Path(self.temp_directory.name) / "ui.db")
        init_db()
        self.paying_student_id = EleveDAO.create("UI-1", "Ada", "Test", "6e", 100000)
        EleveDAO.create("UI-2", "Sam", "Test", "5e", 50000)
        PaiementDAO.add_paiement(self.paying_student_id, 25000, "2026-10-01", "Especes")
        self.window = MainWindow()

    def tearDown(self):
        """Ferme la fenêtre et supprime la base temporaire."""
        self.window.close()
        del self.window
        database_connection.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_filters_by_class_and_payment_status(self):
        """Chaque filtre réduit la liste aux élèves qui correspondent au choix."""
        self.assertEqual(self.window.table.rowCount(), 2)

        self.window.class_filter.setCurrentIndex(self.window.class_filter.findData("6e"))
        self.assertEqual(self.window.table.rowCount(), 1)
        self.assertEqual(int(self.window.table.item(0, 0).text()), self.paying_student_id)

        self.window.class_filter.setCurrentIndex(0)
        self.window.status_filter.setCurrentIndex(self.window.status_filter.findData("En retard"))
        self.assertEqual(self.window.table.rowCount(), 1)
        self.assertEqual(int(self.window.table.item(0, 0).text()), self.paying_student_id + 1)

    def test_navigation_buttons_are_exclusive(self):
        """Un seul bouton de navigation peut rester sélectionné à la fois."""
        buttons = self.window.findChildren(QPushButton, "navButton")
        buttons[0].setChecked(True)
        buttons[1].setChecked(True)

        self.assertEqual(sum(button.isChecked() for button in buttons), 1)


if __name__ == "__main__":
    unittest.main()
