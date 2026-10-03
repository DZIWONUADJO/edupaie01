"""Règles métier qui calculent le solde et le statut de chaque élève."""

from decimal import Decimal

from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO

class EleveService:
    """Prépare des données prêtes à afficher à partir des DAO élèves et paiements."""

    @staticmethod
    def obtenir_liste_eleves_avec_solde():
        """Construit la liste des élèves avec total payé, reste et statut.

        ``Decimal`` sert à éviter les erreurs d'arrondi habituelles des nombres flottants.
        """
        eleves = EleveDAO.get_all()
        resultat = []
        for e in eleves:
            e_id, mat, nom, prenom, classe, frais = e
            frais = Decimal(str(frais))
            total_paye = Decimal(str(PaiementDAO.get_total_paye_par_eleve(e_id)))
            reste = frais - total_paye
            statut = "Crédit" if reste < 0 else ("Soldé" if reste == 0 else ("En retard" if total_paye == 0 else "En cours"))
            resultat.append({
                "id": e_id, "matricule": mat, "nom": nom, "prenom": prenom,
                "classe": classe, "frais": frais, "paye": total_paye,
                "reste": reste, "statut": statut
            })
        return resultat
