"""Charge explicitement le jeu d'exemples EduPaie dans la base SQLite active."""

from pathlib import Path

from src.database.connection import DB_PATH, get_connection, init_db

DEMO_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "demo_data.sql"


def load_demo_data():
    """Ajoute les élèves et paiements fictifs sans supprimer les données existantes.

    Le fichier SQL utilise des matricules DEMO et évite de recréer les mêmes
    paiements si la commande est lancée plusieurs fois.
    """
    init_db()
    with get_connection() as connection:
        with DEMO_DATA_PATH.open("r", encoding="utf-8") as demo_file:
            connection.executescript(demo_file.read())

    with get_connection() as connection:
        student_count = connection.execute(
            "SELECT COUNT(*) FROM eleves WHERE matricule LIKE 'DEMO-%'"
        ).fetchone()[0]
        payment_count = connection.execute(
            "SELECT COUNT(*) FROM paiements "
            "JOIN eleves ON eleves.id = paiements.eleve_id "
            "WHERE eleves.matricule LIKE 'DEMO-%'"
        ).fetchone()[0]

    return student_count, payment_count


def main():
    """Demande une confirmation avant d'ajouter les exemples à la base active."""
    print(f"Base utilisée : {DB_PATH}")
    print("Cette commande ajoute 5 élèves fictifs et leurs paiements; elle ne supprime rien.")
    if input("Tapez OUI pour charger les données de démonstration : ").strip().upper() != "OUI":
        print("Chargement annulé.")
        return

    students, payments = load_demo_data()
    print(f"Jeu de démonstration prêt : {students} élèves DEMO et {payments} paiements.")


if __name__ == "__main__":
    main()
