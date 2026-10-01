import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLineEdit, QLabel, QMessageBox)
from src.database.connection import init_db
from src.services.eleve_service import EleveService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduPaie - Gestion des Frais Scolaires")
        self.resize(900, 550)
        self.init_ui()
        self.charger_donnees()

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
        
        layout.addLayout(search_layout)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Matricule", "Nom", "Prénom", "Classe", "Payé (FCFA)", "Statut"])
        layout.addWidget(self.table)
        
        self.setCentralWidget(main_widget)

    def charger_donnees(self):
        eleves = EleveService.obtenir_liste_eleves_avec_solde()
        filtre = self.search_input.text().lower()
        
        self.table.setRowCount(0)
        for row, e in enumerate(eleves):
            if filtre and filtre not in e["nom"].lower() and filtre not in e["prenom"].lower():
                continue
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(e["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(e["matricule"]))
            self.table.setItem(row, 2, QTableWidgetItem(e["nom"]))
            self.table.setItem(row, 3, QTableWidgetItem(e["prenom"]))
            self.table.setItem(row, 4, QTableWidgetItem(e["classe"]))
            self.table.setItem(row, 5, QTableWidgetItem(f"{e['paye']:,}"))
            self.table.setItem(row, 6, QTableWidgetItem(e["statut"]))

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
