PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS eleve (
    id_eleve INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    date_naissance TEXT NOT NULL,
    classe TEXT NOT NULL,
    annee_scolaire TEXT NOT NULL,
    montant_total_du NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS paiement (
    id_paiement INTEGER PRIMARY KEY AUTOINCREMENT,
    id_eleve INTEGER NOT NULL,
    date_paiement TEXT NOT NULL,
    montant_verse NUMERIC NOT NULL,
    numero_recu TEXT NOT NULL UNIQUE,
    FOREIGN KEY (id_eleve) REFERENCES eleve(id_eleve)
);
