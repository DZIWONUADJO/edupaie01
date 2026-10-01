
from decimal import Decimal, InvalidOperation

from src.database.connection import get_connection

class PaiementDAO:
    @staticmethod
    def add_paiement(eleve_id, montant, date_p, mode_p):
        try:
            montant_decimal = Decimal(str(montant))
        except (InvalidOperation, ValueError) as error:
            raise ValueError("Le montant du paiement est invalide.") from error
        if montant_decimal <= 0:
            raise ValueError("Le montant du paiement doit être positif.")

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT frais_scolarite FROM eleves WHERE id = ?", (eleve_id,))
            eleve = cursor.fetchone()
            if eleve is None:
                raise ValueError("L'élève sélectionné n'existe pas.")
            cursor.execute("SELECT COALESCE(SUM(montant), 0) FROM paiements WHERE eleve_id = ?", (eleve_id,))
            total_paye = Decimal(str(cursor.fetchone()[0]))
            reste = Decimal(str(eleve[0])) - total_paye
            if montant_decimal > reste:
                raise ValueError(f"Le paiement dépasse le reste à payer ({reste:.2f} FCFA).")
            cursor.execute(
                "INSERT INTO paiements (eleve_id, montant, date_paiement, mode_paiement) VALUES (?, ?, ?, ?)",
                (eleve_id, float(montant_decimal), date_p, mode_p)
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
            cursor.execute(
                "SELECT id, montant, date_paiement, mode_paiement "
                "FROM paiements WHERE eleve_id = ? "
                "ORDER BY date_paiement DESC, id DESC",
                (eleve_id,),
            )
            return cursor.fetchall()
