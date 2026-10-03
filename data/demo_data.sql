-- Jeu de données fictif pour tester la recherche, les filtres et le tableau de bord.
-- Les matricules DEMO identifient ces élèves comme des exemples.
BEGIN;

INSERT OR IGNORE INTO eleves (matricule, nom, prenom, classe, frais_scolarite)
VALUES
    ('DEMO-001', 'Exemple', 'Aicha', '6e', 150000),
    ('DEMO-002', 'Demo', 'Malik', '5e', 120000),
    ('DEMO-003', 'Test', 'Sara', '4e', 100000),
    ('DEMO-004', 'Exemple', 'Noah', '3e', 200000),
    ('DEMO-005', 'Demo', 'Ines', '2nde', 175000);

-- Chaque paiement n'est ajouté que s'il n'existe pas déjà, pour rendre le script réutilisable.
INSERT INTO paiements (eleve_id, montant, date_paiement, mode_paiement)
SELECT eleve.id, exemple.montant, exemple.date_paiement, exemple.mode_paiement
FROM eleves AS eleve
JOIN (
    SELECT 'DEMO-001' AS matricule, 50000 AS montant, '2026-09-05' AS date_paiement, 'Espèces' AS mode_paiement
    UNION ALL SELECT 'DEMO-001', 25000, '2026-10-01', 'Mobile Money'
    UNION ALL SELECT 'DEMO-003', 100000, '2026-09-10', 'Virement'
    UNION ALL SELECT 'DEMO-004', 50000, '2026-09-12', 'Chèque'
    UNION ALL SELECT 'DEMO-004', 30000, '2026-10-02', 'Espèces'
    UNION ALL SELECT 'DEMO-005', 175000, '2026-09-08', 'Virement'
) AS exemple ON exemple.matricule = eleve.matricule
WHERE NOT EXISTS (
    SELECT 1
    FROM paiements AS existant
    WHERE existant.eleve_id = eleve.id
      AND existant.montant = exemple.montant
      AND existant.date_paiement = exemple.date_paiement
      AND existant.mode_paiement = exemple.mode_paiement
);

COMMIT;
