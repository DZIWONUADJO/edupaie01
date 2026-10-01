from src.database.connection import get_connection

class EleveDAO:
    @staticmethod
    def create(matricule, nom, prenom, classe, frais):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO eleves (matricule, nom, prenom, classe, frais_scolarite) VALUES (?, ?, ?, ?, ?)",
                (matricule, nom, prenom, classe, frais)
            )
            return cursor.lastrowid

    @staticmethod
    def get_all():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, matricule, nom, prenom, classe, frais_scolarite FROM eleves")
            return cursor.fetchall()

    @staticmethod
    def update(eleve_id, nom, prenom, classe, frais):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE eleves SET nom = ?, prenom = ?, classe = ?, frais_scolarite = ? WHERE id = ?",
                (nom, prenom, classe, frais, eleve_id)
            )

    @staticmethod
    def delete(eleve_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM eleves WHERE id = ?", (eleve_id,))
