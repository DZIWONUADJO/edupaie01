import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton, QMessageBox

from src.database import connection as database_connection
from src.database.connection import init_db
from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO
from src.main_window import MainWindow


class DeleteStudentTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = database_connection.DB_PATH
        database_connection.DB_PATH = str(Path(self.temp_directory.name) / "delete.db")
        init_db()
        self.eleve_id = EleveDAO.create("DEL-1", "Awa", "Test", "6e", 100000)
        PaiementDAO.add_paiement(self.eleve_id, 25000, "2026-10-01", "Especes")
        self.window = MainWindow()
        self.window.table.selectRow(0)
        self.delete_button = self.window.findChild(QPushButton, "dangerButton")

    def tearDown(self):
        self.window.close()
        del self.window
        database_connection.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_delete_button_requires_confirmation(self):
        self.assertIsNotNone(self.delete_button)
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.StandardButton.No):
            self.delete_button.click()

        self.assertEqual(len(EleveDAO.get_all()), 1)
        self.assertEqual(len(PaiementDAO.get_by_eleve(self.eleve_id)), 1)

    def test_confirmed_delete_removes_student_and_associated_payments(self):
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.StandardButton.Yes), \
             patch.object(QMessageBox, "information"):
            self.delete_button.click()

        self.assertEqual(EleveDAO.get_all(), [])
        self.assertEqual(PaiementDAO.get_by_eleve(self.eleve_id), [])


if __name__ == "__main__":
    unittest.main()
