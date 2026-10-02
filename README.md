# EduPaie
# 🎓 EduPaie — Gestion des paiements scolaires

## 📌 Présentation du projet

**EduPaie** est une application desktop de gestion des paiements scolaires développée dans le cadre d'un projet de formation.

L'application permet à un établissement scolaire de gérer les élèves, leurs frais de scolarité et leurs paiements. Elle calcule automatiquement le montant restant à payer et permet de générer un reçu numéroté pour chaque versement.

L'objectif est de remplacer le suivi manuel des paiements effectué dans les cahiers ou les fichiers Excel par une solution simple, fiable et facile à utiliser.

---

## 🎯 Objectifs

EduPaie permet de :

* Enregistrer les élèves et leurs informations.
* Enregistrer le montant total des frais scolaires dus.
* Enregistrer les paiements effectués.
* Calculer automatiquement le total payé et le solde restant.
* Déterminer le statut de paiement d'un élève.
* Consulter l'historique des paiements.
* Générer un reçu unique pour chaque paiement.
* Exporter ou imprimer les reçus en PDF.
* Rechercher et filtrer les élèves.
* Afficher un tableau de bord avec les statistiques de paiement.

---

## ⚙️ Technologies utilisées

| Technologie       | Utilisation                      |
| ----------------- | -------------------------------- |
| Python 3.10+      | Langage de programmation         |
| PySide6           | Interface graphique              |
| SQLite            | Base de données                  |
| ReportLab / FPDF2 | Génération des reçus PDF         |
| QPrinter          | Impression des reçus             |
| Git / GitHub      | Gestion de versions              |
| PyInstaller       | Création de l'exécutable Windows |

---

## 🏗️ Architecture du projet

L'application respecte une architecture en couches afin de séparer clairement les responsabilités.

```text
┌───────────────────────────────┐
│       Interface PySide6       │
│  Fenêtres / Formulaires / UI  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Logique métier         │
│ Validation / Solde / Statut   │
│ Numéro de reçu                │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Repository / DAO        │
│       Requêtes SQL            │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│           SQLite              │
│          edupaie.db           │
└───────────────────────────────┘
```

### Règle importante

Les widgets PySide6 ne communiquent pas directement avec SQLite.

Les requêtes SQL sont regroupées dans les classes **Repository/DAO**.

---

## 📁 Structure du projet

```text
EduPaie/
│
├── main.py
├── requirements.txt
├── README.md
│
├── database/
│   ├── database.py
│   ├── schema.sql
│   └── edupaie.db
│
├── repositories/
│   ├── eleve_repository.py
│   └── paiement_repository.py
│
├── services/
│   ├── eleve_service.py
│   ├── paiement_service.py
│   └── recu_service.py
│
├── ui/
│   ├── main_window.py
│   ├── eleve_form.py
│   ├── paiement_dialog.py
│   └── eleve_detail.py
│
├── receipts/
│   └── ...
│
└── resources/
    └── icons/
```

---

# 🗄️ Base de données

EduPaie utilise **SQLite**.

La base contient notamment les tables :

### Table `eleves`

Elle contient les informations concernant les élèves.

```text
id
nom
prenom
classe
annee_scolaire
montant_total_du
```

### Table `paiements`

Elle contient les informations concernant les paiements.

```text
id
id_eleve
numero_recu
montant
date_paiement
mode_paiement
```

### Relation

```text
ELEVE
  │
  │ 1
  │
  │ N
  ▼
PAIEMENT
```

Un élève peut donc effectuer plusieurs paiements.

---

# 💰 Calcul du solde

Le solde restant est calculé automatiquement.

```text
Solde = Total dû - Total des paiements
```

### Exemple

Un élève doit :

```text
Total dû : 300 000 FCFA
```

Il a payé :

```text
100 000 FCFA
```

Le système affiche :

```text
Total payé : 100 000 FCFA
Solde :      200 000 FCFA
Statut :     Partiellement payé
```

---

# 📊 Statuts de paiement

EduPaie utilise trois statuts principaux :

### 🟢 Soldé

L'élève a payé la totalité des frais.

```text
Solde = 0 FCFA
```

### 🟠 Partiellement payé

L'élève a effectué au moins un paiement mais il reste encore une somme à payer.

```text
Solde > 0
```

### 🔴 Non payé

Aucun paiement n'a encore été effectué.

```text
Total payé = 0 FCFA
```

---

# 💳 Modes de paiement

L'application accepte les modes suivants :

* Espèces
* Chèque
* Virement
* Mobile Money

---

# 🧾 Gestion des reçus

Chaque paiement enregistré génère un reçu possédant un **numéro unique**.

Exemple :

```text
RCP-0001
RCP-0002
RCP-0003
```

Le reçu contient :

* Numéro du reçu
* Nom et prénom de l'élève
* Classe
* Année scolaire
* Montant payé
* Date du paiement
* Mode de paiement
* Solde restant après paiement

Le reçu peut être :

* consulté ;
* réimprimé ;
* exporté au format PDF.

---

# 🔐 Validation des paiements

Avant d'enregistrer un paiement, l'application vérifie que :

* le montant est renseigné ;
* le montant est numérique ;
* le montant est supérieur à zéro ;
* la date est valide ;
* le mode de paiement est renseigné ;
* le montant ne dépasse pas le solde restant.

### Exemple

Si le solde est :

```text
120 000 FCFA
```

et que l'utilisateur saisit :

```text
150 000 FCFA
```

l'application affiche un message d'avertissement et refuse l'enregistrement.

---

# 🖥️ Fonctionnalités principales

## 1. Tableau de bord

Le tableau de bord affiche :

* nombre total d'élèves ;
* total encaissé ;
* total restant dû ;
* nombre d'élèves non soldés ;
* liste des élèves selon leur statut.

---

## 2. Gestion des élèves

L'utilisateur peut :

* ajouter un élève ;
* modifier un élève ;
* supprimer un élève ;
* rechercher un élève ;
* filtrer les élèves par classe.

---

## 3. Fiche élève

La fiche d'un élève affiche :

```text
Nom
Prénom
Classe
Année scolaire
Total dû
Total payé
Solde
Statut
```

Elle contient également l'historique de tous les paiements.

---

## 4. Paiements

L'utilisateur peut enregistrer :

```text
Élève
Montant
Date
Mode de paiement
```

Après validation, le paiement est enregistré et le solde est automatiquement recalculé.

---

## 5. Historique

Pour chaque élève, l'utilisateur peut consulter tous les paiements effectués.

Exemple :

| Reçu     | Date       |   Montant | Mode         |     Solde |
| -------- | ---------- | --------: | ------------ | --------: |
| RCP-0001 | 01/09/2026 | 100 000 F | Espèces      | 200 000 F |
| RCP-0008 | 15/09/2026 | 100 000 F | Mobile Money | 100 000 F |
| RCP-0015 | 30/09/2026 | 100 000 F | Virement     |       0 F |

---

# 🚀 Installation

## Prérequis

Pour développer et exécuter le projet depuis les sources, il faut :

* Python 3.10 ou une version supérieure ;
* Git ;
* Windows recommandé pour la génération de l'exécutable.

---

## 1. Cloner le projet

```bash
git clone https://github.com/VOTRE-NOM/EduPaie.git
```

Puis :

```bash
cd EduPaie
```

---

## 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### Sous Windows

```bash
venv\Scripts\activate
```

---

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 4. Initialiser la base de données

La base SQLite est située dans :

```text
database/edupaie.db
```

Si la base n'existe pas, exécuter le script de création :

```bash
python database/database.py
```

---

## 5. Lancer l'application

```bash
python main.py
```

L'application EduPaie devrait alors s'ouvrir.

---

# 🧪 Jeu de données de test

Le projet contient une base SQLite pré-remplie avec au minimum **15 élèves**.

Les données comprennent plusieurs situations :

```text
Élèves soldés
Élèves partiellement payés
Élèves non payés
```

Cela permet de tester les différents statuts et le tableau de bord.

---

# 📦 Génération de l'exécutable Windows

Pour créer une version utilisable sur une machine ne possédant pas Python :

```bash
pip install pyinstaller
```

Puis :

```bash
pyinstaller --onefile --windowed main.py
```

L'exécutable sera généré dans :

```text
dist/
```

Le fichier sera :

```text
dist/main.exe
```

Il peut ensuite être renommé :

```text
EduPaie.exe
```

---

# 🔧 Tests

Avant la livraison, les fonctionnalités suivantes doivent être testées :

* [ ] Ajouter un élève
* [ ] Modifier un élève
* [ ] Supprimer un élève
* [ ] Rechercher un élève
* [ ] Filtrer par classe
* [ ] Enregistrer un paiement
* [ ] Refuser un paiement supérieur au solde
* [ ] Calculer automatiquement le solde
* [ ] Afficher le statut de paiement
* [ ] Consulter l'historique
* [ ] Générer un reçu
* [ ] Réimprimer un reçu
* [ ] Exporter un reçu PDF
* [ ] Vérifier le tableau de bord
* [ ] Tester les messages d'erreur

---

# 🌳 Gestion Git

Le projet doit être versionné avec Git.

Exemple :

```bash
git init
```

Premier commit :

```bash
git add .
git commit -m "Initialisation du projet EduPaie"
```

Puis des commits réguliers :

```bash
git add .
git commit -m "Ajout de la base de données SQLite"

git add .
git commit -m "Ajout de la gestion des élèves"

git add .
git commit -m "Ajout de l'enregistrement des paiements"

git add .
git commit -m "Ajout du calcul automatique du solde"

git add .
git commit -m "Ajout de la génération des reçus"

git add .
git commit -m "Ajout du tableau de bord"

git add .
git commit -m "Préparation du packaging Windows"
```

---

# 👩‍💻 Auteur

**Projet : EduPaie**

Application de gestion des paiements scolaires.

**Développé avec :**


Python
PySide6
SQLite
```

---

# 📚 Contexte pédagogique

Ce projet a été réalisé dans le cadre de la formation :

**Développeur Web et Web Mobile**

Il permet de mettre en pratique :

* la programmation Python ;
* la programmation orientée objet ;
* la conception d'une base de données relationnelle ;
* SQL ;
* les interfaces graphiques avec PySide6 ;
* la séparation des couches d'une application ;
* la génération de documents PDF ;
* Git et GitHub ;
* le déploiement d'une application desktop.

---

# ⚠️ Limites connues

Cette première version est destinée à la gestion interne d'un établissement.

Les fonctionnalités suivantes peuvent être ajoutées ultérieurement :

* gestion de plusieurs établissements ;
* gestion des utilisateurs et des rôles ;
* sauvegarde automatique de la base ;
* statistiques avancées ;
* export Excel ;
* notifications ;
* gestion des dépenses de l'établissement ;
* synchronisation avec une base de données distante.

---

# 📄 Licence

Projet réalisé dans un cadre pédagogique.
