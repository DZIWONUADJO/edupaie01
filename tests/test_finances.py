"""Tests métier des calculs de solde et des paiements."""

import tempfile
import unittest
from pathlib import Path

import src.database.connection as connection_module
from src.database.connection import init_db
from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO
from src.services.eleve_service import EleveService


class FinancesTestCase(unittest.TestCase):
    """Les tests utilisent une base temporaire pour ne pas toucher aux données réelles."""

    def setUp(self):
        """Initialise la base de test et crée un élève."""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = connection_module.DB_PATH
        connection_module.DB_PATH = str(Path(self.temp_directory.name) / "test.db")
        init_db()
        self.eleve_id = EleveDAO.create("E-TEST", "Nom", "Prenom", "6e", 100000)

    def tearDown(self):
        """Rétablit le chemin de la base active et nettoie le dossier temporaire."""
        connection_module.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_solde_et_ordre_des_paiements(self):
        """Le reste est exact et le paiement le plus récent apparaît en premier."""
        PaiementDAO.add_paiement(self.eleve_id, "25000.50", "2026-09-01", "Especes")
        PaiementDAO.add_paiement(self.eleve_id, "10000.25", "2026-10-01", "Virement")

        paiements = PaiementDAO.get_by_eleve(self.eleve_id)
        solde = EleveService.obtenir_liste_eleves_avec_solde()[0]

        self.assertEqual(paiements[0][2], "2026-10-01")
        self.assertEqual(solde["reste"], 64999.25)

    def test_surpaiement_refuse(self):
        """Un versement supérieur aux frais restants doit lever une erreur."""
        with self.assertRaises(ValueError):
            PaiementDAO.add_paiement(self.eleve_id, 100001, "2026-10-01", "Especes")


if __name__ == "__main__":
    unittest.main()
