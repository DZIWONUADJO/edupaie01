-- Active les clés étrangères : SQLite ne les applique pas par défaut.
PRAGMA foreign_keys = ON;

-- Un élève peut avoir plusieurs paiements enregistrés dans la table suivante.
CREATE TABLE IF NOT EXISTS eleves (
    -- Identifiant interne créé automatiquement par SQLite.
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule TEXT NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    classe TEXT NOT NULL,
    frais_scolarite NUMERIC NOT NULL CHECK (frais_scolarite >= 0)
);

CREATE TABLE IF NOT EXISTS paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eleve_id INTEGER NOT NULL,
    montant NUMERIC NOT NULL CHECK (montant > 0),
    date_paiement TEXT NOT NULL,
    mode_paiement TEXT NOT NULL,
    -- La suppression d'un élève supprime aussi tous ses paiements associés.
    FOREIGN KEY (eleve_id) REFERENCES eleves(id) ON DELETE CASCADE
);
