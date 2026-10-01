
from src.database.connection import get_connection

class PaiementDAO:
    @staticmethod
    def add_paiement(eleve_id, montant, date_p, mode_p):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO paiements (eleve_id, montant, date_paiement, mode_paiement) VALUES (?, ?, ?, ?)",
                (eleve_id, montant, date_p, mode_p)
            )
            return cursor.lastrowid

    @staticmethod
    def get_total_paye_par_eleve(eleve_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(montant), 0) FROM paiements WHERE eleve_id = ?", (eleve_id,))
            return cursor.fetchone()[0]

    @staticmethod
    def get_by_eleve(eleve_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, montant, date_paiement, mode_paiement FROM paiements WHERE eleve_id = ?", (eleve_id,))
            return cursor.fetchall()
