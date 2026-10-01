from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO

class EleveService:
    @staticmethod
    def obtenir_liste_eleves_avec_solde():
        eleves = EleveDAO.get_all()
        resultat = []
        for e in eleves:
            e_id, mat, nom, prenom, classe, frais = e
            total_paye = PaiementDAO.get_total_paye_par_eleve(e_id)
            reste = frais - total_paye
            statut = "Soldé" if reste <= 0 else ("En retard" if total_paye == 0 else "En cours")
            resultat.append({
                "id": e_id, "matricule": mat, "nom": nom, "prenom": prenom,
                "classe": classe, "frais": frais, "paye": total_paye,
                "reste": max(0, reste), "statut": statut
            })
        return resultat
