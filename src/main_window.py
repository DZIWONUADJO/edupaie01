import sys
import os
from decimal import Decimal
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLineEdit, QLabel, QMessageBox,
                             QDialog, QFormLayout, QComboBox, QDoubleSpinBox,
                             QDateEdit, QDialogButtonBox, QAbstractItemView)
from PySide6.QtCore import QDate
from src.database.connection import init_db
from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO
from src.services.eleve_service import EleveService
from src.services.pdf_service import PDFService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduPaie - Gestion des Frais Scolaires")
        self.resize(900, 550)
        self.init_ui()
        self.charger_donnees()

    @staticmethod
    def format_montant(montant):
        return f"{Decimal(str(montant)):,.2f} FCFA"

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un élève par nom...")
        self.search_input.textChanged.connect(self.charger_donnees)
        search_layout.addWidget(QLabel("🔍 Recherche :"))
        search_layout.addWidget(self.search_input)

        add_student_button = QPushButton("Ajouter un élève")
        add_student_button.clicked.connect(self.ajouter_eleve)
        search_layout.addWidget(add_student_button)

        add_payment_button = QPushButton("Enregistrer un paiement")
        add_payment_button.clicked.connect(self.ajouter_paiement)
        search_layout.addWidget(add_payment_button)

        receipt_button = QPushButton("Générer la facture PDF")
        receipt_button.clicked.connect(self.generer_facture)
        search_layout.addWidget(receipt_button)
        
        layout.addLayout(search_layout)

        dashboard_layout = QHBoxLayout()
        self.total_eleves_label = QLabel()
        self.total_du_label = QLabel()
        self.total_paye_label = QLabel()
        self.total_reste_label = QLabel()
        for label in (self.total_eleves_label, self.total_du_label, self.total_paye_label, self.total_reste_label):
            dashboard_layout.addWidget(label)
        layout.addLayout(dashboard_layout)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Matricule", "Nom", "Prénom", "Classe", "Dû", "Payé", "Reste"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.cellDoubleClicked.connect(lambda row, _column: self.generer_facture(row))
        layout.addWidget(self.table)
        
        self.setCentralWidget(main_widget)

    def charger_donnees(self):
        eleves = EleveService.obtenir_liste_eleves_avec_solde()
        filtre = self.search_input.text().lower()

        total_du = sum(e["frais"] for e in eleves)
        total_paye = sum(e["paye"] for e in eleves)
        self.total_eleves_label.setText(f"Élèves : {len(eleves)}")
        self.total_du_label.setText(f"Total dû : {self.format_montant(total_du)}")
        self.total_paye_label.setText(f"Total payé : {self.format_montant(total_paye)}")
        self.total_reste_label.setText(f"Reste : {self.format_montant(total_du - total_paye)}")
        
        self.table.setRowCount(0)
        for e in eleves:
            if filtre and filtre not in e["nom"].lower() and filtre not in e["prenom"].lower():
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(e["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(e["matricule"]))
            self.table.setItem(row, 2, QTableWidgetItem(e["nom"]))
            self.table.setItem(row, 3, QTableWidgetItem(e["prenom"]))
            self.table.setItem(row, 4, QTableWidgetItem(e["classe"]))
            self.table.setItem(row, 5, QTableWidgetItem(self.format_montant(e["frais"])))
            self.table.setItem(row, 6, QTableWidgetItem(self.format_montant(e["paye"])))
            self.table.setItem(row, 7, QTableWidgetItem(self.format_montant(e["reste"])))

    def generer_facture(self, row=None):
        if row is None:
            selected_rows = self.table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.information(self, "Sélection nécessaire", "Sélectionnez une ligne élève pour générer sa facture.")
                return
            row = selected_rows[0].row()

        eleve_id = int(self.table.item(row, 0).text())
        donnees = next((item for item in EleveService.obtenir_liste_eleves_avec_solde() if item["id"] == eleve_id), None)
        eleve = next((item for item in EleveDAO.get_all() if item[0] == eleve_id), None)
        if eleve is None or donnees is None:
            QMessageBox.warning(self, "Élève introuvable", "L'élève sélectionné n'existe plus.")
            return

        paiements = PaiementDAO.get_by_eleve(eleve_id)
        dernier_paiement = paiements[0] if paiements else None
        facture_no = f"FAC-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{eleve_id:04d}"
        try:
            filename = PDFService.generer_facture(
                eleve[1], eleve[2], eleve[3], eleve[4],
                donnees["frais"], donnees["paye"], donnees["reste"],
                dernier_paiement, facture_no
            )
        except Exception as error:
            QMessageBox.critical(self, "Génération impossible", f"Le reçu n'a pas été généré : {error}")
            return
        QMessageBox.information(self, "Facture générée", f"La facture PDF a été créée ici :\n{filename}")

    def ajouter_eleve(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un élève")
        form = QFormLayout(dialog)

        matricule = QLineEdit()
        nom = QLineEdit()
        prenom = QLineEdit()
        classe = QLineEdit()
        frais = QDoubleSpinBox()
        frais.setRange(0, 1_000_000_000)
        frais.setDecimals(2)
        frais.setSuffix(" FCFA")

        form.addRow("Matricule :", matricule)
        form.addRow("Nom :", nom)
        form.addRow("Prénom :", prenom)
        form.addRow("Classe :", classe)
        form.addRow("Frais de scolarité :", frais)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = [matricule.text().strip(), nom.text().strip(), prenom.text().strip(), classe.text().strip()]
        if not all(values):
            QMessageBox.warning(self, "Informations manquantes", "Tous les champs de l'élève sont obligatoires.")
            return
        try:
            EleveDAO.create(*values, frais.value())
        except Exception as error:
            QMessageBox.critical(self, "Ajout impossible", f"L'élève n'a pas été ajouté : {error}")
            return
        self.charger_donnees()

    def ajouter_paiement(self):
        eleves = EleveDAO.get_all()
        if not eleves:
            QMessageBox.information(self, "Aucun élève", "Ajoutez d'abord un élève avant d'enregistrer un paiement.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Enregistrer un paiement")
        form = QFormLayout(dialog)

        eleve = QComboBox()
        for item in eleves:
            eleve.addItem(f"{item[1]} - {item[2]} {item[3]}", item[0])
        montant = QDoubleSpinBox()
        montant.setRange(0.01, 1_000_000_000)
        montant.setDecimals(2)
        montant.setSuffix(" FCFA")
        date_paiement = QDateEdit(QDate.currentDate())
        date_paiement.setCalendarPopup(True)
        mode = QComboBox()
        mode.addItems(["Espèces", "Virement", "Chèque", "Mobile Money"])

        form.addRow("Élève :", eleve)
        form.addRow("Montant :", montant)
        form.addRow("Date :", date_paiement)
        form.addRow("Mode de paiement :", mode)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            PaiementDAO.add_paiement(
                eleve.currentData(),
                montant.value(),
                date_paiement.date().toString("yyyy-MM-dd"),
                mode.currentText(),
            )
        except Exception as error:
            QMessageBox.critical(self, "Paiement impossible", f"Le paiement n'a pas été enregistré : {error}")
            return
        self.charger_donnees()

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
