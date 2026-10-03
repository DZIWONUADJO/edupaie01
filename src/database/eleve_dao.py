"""DAO (accès aux données) : toutes les requêtes SQL liées aux élèves."""

from src.database.connection import get_connection

class EleveDAO:
    """Fournit les opérations de lecture et d'écriture pour la table ``eleves``."""

    @staticmethod
    def create(matricule, nom, prenom, classe, frais):
        """Ajoute un élève et retourne l'identifiant créé par SQLite."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO eleves (matricule, nom, prenom, classe, frais_scolarite) VALUES (?, ?, ?, ?, ?)",
                (matricule, nom, prenom, classe, frais)
            )
            return cursor.lastrowid

    @staticmethod
    def get_all():
        """Retourne les élèves sous forme de lignes SQLite dans un ordre stable."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, matricule, nom, prenom, classe, frais_scolarite FROM eleves")
            return cursor.fetchall()

    @staticmethod
    def update(eleve_id, nom, prenom, classe, frais):
        """Modifie les informations scolaires de l'élève indiqué par son ID."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE eleves SET nom = ?, prenom = ?, classe = ?, frais_scolarite = ? WHERE id = ?",
                (nom, prenom, classe, frais, eleve_id)
            )

    @staticmethod
    def delete(eleve_id):
        """Supprime l'élève; SQLite supprime aussi ses paiements liés (cascade)."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM eleves WHERE id = ?", (eleve_id,))
