"""Fenêtre principale EduPaie et branchement des actions de l'interface."""

import sys
import os
from decimal import Decimal
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLineEdit, QLabel, QMessageBox,
                             QDialog, QFormLayout, QComboBox, QDoubleSpinBox,
                             QDateEdit, QDialogButtonBox, QAbstractItemView,
                             QFrame, QGridLayout, QHeaderView, QButtonGroup,
                             QFileDialog)
from PySide6.QtCore import QDate, QRect, Qt
from PySide6.QtGui import QPainter, QFont, QFontDatabase, QColor
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from src.database.connection import DB_PATH, init_db
from src.database.backup import create_backup, restore_backup
from src.database.eleve_dao import EleveDAO
from src.database.paiement_dao import PaiementDAO
from src.services.eleve_service import EleveService
from src.services.pdf_service import PDFService

class MainWindow(QMainWindow):
    """Construit le tableau de bord et relie les boutons aux services métier."""

    # Cette feuille de style Qt (QSS) définit les couleurs et tailles des widgets.
    APP_STYLE = """
        QWidget#appRoot { background: #f1f3f2; color: #26332d; font-family: "Segoe UI"; font-size: 10pt; }
        QFrame#topBar { background: #08784e; }
        QLabel#brand { color: white; font-size: 19pt; font-weight: 700; }
        QLabel#topBarSubtitle { color: #d4eee2; font-size: 9pt; }
        QFrame#sidebar { background: #ffffff; border-right: 1px solid #dce4df; }
        QLabel#sidebarHeading { color: #7b8982; font-size: 8pt; font-weight: 700; padding: 12px 12px 5px; }
        QPushButton#navButton { text-align: left; background: transparent; color: #48564f; border: 0; border-left: 3px solid transparent; padding: 10px 12px; border-radius: 0; }
        QPushButton#navButton:hover { background: #edf6f1; color: #08784e; }
        QPushButton#navButton:pressed, QPushButton#navButton:checked { background: #e5f2eb; color: #08784e; border-left: 3px solid #08784e; font-weight: 700; }
        QLabel#pageTitle { color: #26332d; font-size: 19pt; font-weight: 650; }
        QLabel#sectionTitle { color: #08784e; font-size: 12pt; font-weight: 700; }
        QLabel#mutedText { color: #78867f; }
        QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox { background: white; border: 1px solid #d7e0db; border-radius: 4px; padding: 8px 10px; selection-background-color: #08784e; }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus { border: 1px solid #08784e; }
        QPushButton#primaryButton { background: #08784e; color: white; border: 1px solid #08784e; border-radius: 4px; padding: 9px 12px; font-weight: 600; }
        QPushButton#primaryButton:hover { background: #066540; }
        QPushButton#primaryButton:pressed { background: #045333; }
        QPushButton#secondaryButton { background: #e9efeb; color: #33443a; border: 1px solid #dce5df; border-radius: 4px; padding: 8px 12px; }
        QPushButton#secondaryButton:hover { background: #dcebe2; color: #08784e; }
        QPushButton#dangerButton { text-align: left; background: #fff1f0; color: #a52a22; border: 1px solid #f1d0cd; border-radius: 4px; padding: 9px 12px; font-weight: 600; }
        QPushButton#dangerButton:hover { background: #ffe4e1; border-color: #e8b6b1; }
        QFrame#metricCard { background: white; border: 1px solid #e1e7e3; border-radius: 5px; }
        QLabel#metricTitle { color: #708078; font-size: 9pt; }
        QLabel#metricValue { color: #08784e; font-size: 15pt; font-weight: 700; }
        QTableWidget { background: white; alternate-background-color: #f8faf9; border: 1px solid #e1e7e3; border-radius: 5px; gridline-color: #edf0ee; selection-background-color: #e4f2e9; selection-color: #174d35; }
        QHeaderView::section { background: #f5f8f6; color: #53645b; border: 0; border-bottom: 1px solid #dce4df; padding: 10px 8px; font-weight: 700; }
        QTableWidget::item { padding: 7px; border-bottom: 1px solid #eff2f0; }
        QDialog, QMessageBox { background: #f7f9f8; }
        QDialogButtonBox QPushButton, QMessageBox QPushButton { min-width: 80px; padding: 7px 12px; }
    """

    def __init__(self):
        super().__init__()
        self.charger_polices_systeme()
        self.setWindowTitle("EduPaie - Gestion des Frais Scolaires")
        self.resize(1180, 720)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(self.APP_STYLE)
        self.init_ui()
        self.charger_donnees()

    @staticmethod
    def charger_polices_systeme():
        """Charge Segoe UI depuis Windows pour afficher correctement le français."""
        for font_path in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"):
            if os.path.exists(font_path):
                QFontDatabase.addApplicationFont(font_path)

    @staticmethod
    def format_montant(montant):
        """Présente un nombre avec deux décimales et l'unité monétaire FCFA."""
        return f"{Decimal(str(montant)):,.2f} FCFA"

    def init_ui(self):
        """Crée le bandeau, le menu, les filtres, les indicateurs et le tableau."""
        main_widget = QWidget()
        main_widget.setObjectName("appRoot")
        root_layout = QVBoxLayout(main_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Bandeau supérieur : identité de l'application et titre du logiciel.
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(62)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        brand = QLabel("EduPaie")
        brand.setObjectName("brand")
        top_layout.addWidget(brand)
        top_layout.addStretch()
        subtitle = QLabel("GESTION DES FRAIS SCOLAIRES")
        subtitle.setObjectName("topBarSubtitle")
        top_layout.addWidget(subtitle)
        root_layout.addWidget(top_bar)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Le menu latéral regroupe les commandes par thème.
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(205)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 16, 0, 16)
        sidebar_layout.setSpacing(3)
        self.navigation_group = QButtonGroup(self)
        self.navigation_group.setExclusive(True)
        actions_heading = QLabel("ACTIONS")
        actions_heading.setObjectName("sidebarHeading")
        sidebar_layout.addWidget(actions_heading)

        dashboard_button = self.creer_bouton_menu("Vue d'ensemble", self.afficher_tous_les_eleves, checked=True)
        sidebar_layout.addWidget(dashboard_button)
        sidebar_layout.addWidget(self.creer_bouton_menu("Nouvel élève", self.ajouter_eleve))

        payment_heading = QLabel("PAIEMENTS")
        payment_heading.setObjectName("sidebarHeading")
        sidebar_layout.addWidget(payment_heading)
        sidebar_layout.addWidget(self.creer_bouton_menu("Historique paiements", self.afficher_historique))
        sidebar_layout.addWidget(self.creer_bouton_menu("Imprimer reçu", self.imprimer_recu))

        documents_heading = QLabel("DOCUMENTS")
        documents_heading.setObjectName("sidebarHeading")
        sidebar_layout.addWidget(documents_heading)
        sidebar_layout.addWidget(self.creer_bouton_menu("Facture PDF", self.generer_facture))
        data_heading = QLabel("DONNÉES")
        data_heading.setObjectName("sidebarHeading")
        sidebar_layout.addWidget(data_heading)
        sidebar_layout.addWidget(self.creer_bouton_menu("Sauvegarder", self.sauvegarder_base))
        sidebar_layout.addWidget(self.creer_bouton_menu("Restaurer", self.restaurer_base))
        management_heading = QLabel("GESTION")
        management_heading.setObjectName("sidebarHeading")
        sidebar_layout.addWidget(management_heading)
        delete_button = QPushButton("Supprimer l'élève")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(self.supprimer_eleve)
        sidebar_layout.addWidget(delete_button)
        sidebar_layout.addStretch()
        body_layout.addWidget(sidebar)

        # La zone centrale affiche les filtres et les informations de suivi.
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(26, 22, 26, 24)
        content_layout.setSpacing(16)

        title_row = QHBoxLayout()
        title = QLabel("Vue d'ensemble")
        title.setObjectName("pageTitle")
        title_row.addWidget(title)
        title_row.addStretch()
        new_payment_button = QPushButton("Nouveau paiement")
        new_payment_button.setObjectName("primaryButton")
        new_payment_button.clicked.connect(self.ajouter_paiement)
        title_row.addWidget(new_payment_button)
        content_layout.addLayout(title_row)

        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un élève...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.charger_donnees)
        filter_row.addWidget(self.search_input)
        class_label = QLabel("Classe")
        class_label.setObjectName("mutedText")
        filter_row.addWidget(class_label)
        self.class_filter = QComboBox()
        self.class_filter.setFixedWidth(160)
        self.class_filter.addItem("Toutes les classes", "")
        self.class_filter.currentIndexChanged.connect(self.charger_donnees)
        filter_row.addWidget(self.class_filter)
        status_label = QLabel("Statut")
        status_label.setObjectName("mutedText")
        filter_row.addWidget(status_label)
        self.status_filter = QComboBox()
        self.status_filter.setFixedWidth(150)
        self.status_filter.addItem("Tous les statuts", "")
        for status in ("En retard", "En cours", "Soldé", "Crédit"):
            self.status_filter.addItem(status, status)
        self.status_filter.currentIndexChanged.connect(self.charger_donnees)
        filter_row.addWidget(self.status_filter)
        filter_row.addStretch()
        content_layout.addLayout(filter_row)

        # Chaque carte reçoit sa valeur depuis charger_donnees().
        metrics = QGridLayout()
        metrics.setHorizontalSpacing(12)
        metrics.setVerticalSpacing(12)
        self.total_eleves_label = self.creer_carte_indicateur(metrics, 0, 0, "ÉLÈVES")
        self.total_du_label = self.creer_carte_indicateur(metrics, 0, 1, "TOTAL DÛ")
        self.total_paye_label = self.creer_carte_indicateur(metrics, 0, 2, "TOTAL PAYÉ")
        self.total_reste_label = self.creer_carte_indicateur(metrics, 0, 3, "RESTE À PAYER")
        content_layout.addLayout(metrics)

        table_heading = QHBoxLayout()
        section_title = QLabel("Suivi des élèves")
        section_title.setObjectName("sectionTitle")
        table_heading.addWidget(section_title)
        table_heading.addStretch()
        content_layout.addLayout(table_heading)

        # L'ID reste dans le tableau pour retrouver l'élève, mais n'est pas visible.
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Matricule", "Nom", "Prénom", "Classe", "Dû", "Payé", "Reste", "Statut"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(0, True)
        self.table.cellDoubleClicked.connect(lambda row, _column: self.generer_facture(row))
        content_layout.addWidget(self.table)

        body_layout.addWidget(content, 1)
        root_layout.addWidget(body, 1)
        
        self.setCentralWidget(main_widget)

    def creer_bouton_menu(self, texte, action, checked=False):
        """Crée un bouton du menu et relie son clic à une méthode de la fenêtre."""
        button = QPushButton(texte)
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setChecked(checked)
        self.navigation_group.addButton(button)
        button.clicked.connect(action)
        return button

    def creer_carte_indicateur(self, grid, row, column, titre):
        """Ajoute une carte de statistique et retourne son étiquette de valeur."""
        card = QFrame()
        card.setObjectName("metricCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 14)
        card_layout.setSpacing(7)
        title = QLabel(titre)
        title.setObjectName("metricTitle")
        value = QLabel("0")
        value.setObjectName("metricValue")
        card_layout.addWidget(title)
        card_layout.addWidget(value)
        grid.addWidget(card, row, column)
        return value

    def afficher_tous_les_eleves(self):
        """Efface les filtres pour revenir à la liste complète des élèves."""
        self.search_input.blockSignals(True)
        self.class_filter.blockSignals(True)
        self.status_filter.blockSignals(True)
        self.search_input.clear()
        self.class_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.search_input.blockSignals(False)
        self.class_filter.blockSignals(False)
        self.status_filter.blockSignals(False)
        self.charger_donnees()

    def charger_donnees(self):
        """Rafraîchit les totaux et affiche les élèves qui correspondent aux filtres."""
        eleves = EleveService.obtenir_liste_eleves_avec_solde()
        filtre = self.search_input.text().lower()

        # Les choix de classe disponibles sont construits depuis les élèves en base.
        classe_selectionnee = self.class_filter.currentData()
        classes = sorted({e["classe"] for e in eleves}, key=str.casefold)
        if [self.class_filter.itemText(i) for i in range(1, self.class_filter.count())] != classes:
            self.class_filter.blockSignals(True)
            self.class_filter.clear()
            self.class_filter.addItem("Toutes les classes", "")
            for class_name in classes:
                self.class_filter.addItem(class_name, class_name)
            selected_index = self.class_filter.findData(classe_selectionnee)
            self.class_filter.setCurrentIndex(max(0, selected_index))
            self.class_filter.blockSignals(False)

        classe_selectionnee = self.class_filter.currentData()
        statut_selectionne = self.status_filter.currentData()

        # Les cartes restent des totaux généraux, même quand le tableau est filtré.
        total_du = sum(e["frais"] for e in eleves)
        total_paye = sum(e["paye"] for e in eleves)
        self.total_eleves_label.setText(str(len(eleves)))
        self.total_du_label.setText(self.format_montant(total_du))
        self.total_paye_label.setText(self.format_montant(total_paye))
        self.total_reste_label.setText(self.format_montant(total_du - total_paye))
        
        self.table.setRowCount(0)
        for e in eleves:
            # La recherche accepte le nom, le prénom ou le matricule.
            texte_eleve = f"{e['nom']} {e['prenom']} {e['matricule']}".lower()
            if filtre and filtre not in texte_eleve:
                continue
            if classe_selectionnee and e["classe"] != classe_selectionnee:
                continue
            if statut_selectionne and e["statut"] != statut_selectionne:
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
            status_item = QTableWidgetItem(e["statut"])
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_colors = {
                "En retard": ("#8a5700", "#fff1d2"),
                "En cours": ("#245b86", "#e8f2fa"),
                "Soldé": ("#08784e", "#e5f3eb"),
                "Crédit": ("#176c70", "#e4f3f2"),
            }
            foreground, background = status_colors.get(e["statut"], ("#53645b", "#f1f4f2"))
            status_item.setForeground(QColor(foreground))
            status_item.setBackground(QColor(background))
            self.table.setItem(row, 8, status_item)

    def sauvegarder_base(self):
        """Demande un emplacement puis copie la base SQLite à cet endroit."""
        default_path = os.path.join(
            os.path.dirname(DB_PATH),
            f"edupaie_sauvegarde_{datetime.now().strftime('%Y%m%d-%H%M%S')}.db",
        )
        destination, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder la base EduPaie", default_path, "Base SQLite (*.db)"
        )
        if not destination:
            return
        if not destination.lower().endswith(".db"):
            destination += ".db"
        try:
            saved_path = create_backup(destination)
        except Exception as error:
            QMessageBox.critical(self, "Sauvegarde impossible", str(error))
            return
        QMessageBox.information(self, "Sauvegarde terminée", f"Copie créée ici :\n{saved_path}")

    def restaurer_base(self):
        """Confirme puis restaure une sauvegarde après vérification et copie de sécurité."""
        backup_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une sauvegarde EduPaie", os.path.dirname(DB_PATH), "Base SQLite (*.db)"
        )
        if not backup_path:
            return

        answer = QMessageBox.question(
            self,
            "Confirmer la restauration",
            "La restauration remplacera les données actuelles. Une copie de sécurité "
            "de la base actuelle sera créée avant le remplacement. Continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            safety_path = restore_backup(backup_path)
            init_db()
            self.charger_donnees()
        except Exception as error:
            QMessageBox.critical(self, "Restauration impossible", str(error))
            return
        QMessageBox.information(
            self,
            "Restauration terminée",
            f"La base a été restaurée. Copie de sécurité :\n{safety_path}",
        )

    def modifier_eleve(self):
        """Ouvre un formulaire prérempli et enregistre les modifications de l'élève."""
        eleve = self.obtenir_eleve_selectionne()
        if eleve is None:
            return

        # eleve = (id, matricule, nom, prenom, classe, frais_scolarite)
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier un élève")
        form = QFormLayout(dialog)

        matricule_label = QLabel(eleve[1])
        matricule_label.setObjectName("mutedText")
        nom = QLineEdit(eleve[2])
        prenom = QLineEdit(eleve[3])
        classe = QLineEdit(eleve[4])
        frais = QDoubleSpinBox()
        frais.setRange(0, 1_000_000_000)
        frais.setDecimals(2)
        frais.setSuffix(" FCFA")
        frais.setValue(float(eleve[5]))

        form.addRow("Matricule :", matricule_label)
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

        values = [nom.text().strip(), prenom.text().strip(), classe.text().strip()]
        if not all(values):
            QMessageBox.warning(self, "Informations manquantes", "Le nom, prénom et classe sont obligatoires.")
            return

        try:
            EleveDAO.update(eleve[0], values[0], values[1], values[2], frais.value())
        except Exception as error:
            QMessageBox.critical(self, "Modification impossible", f"L'élève n'a pas été modifié : {error}")
            return

        self.charger_donnees()
        QMessageBox.information(self, "Élève modifié", f"{values[0]} {values[1]} a été mis à jour.")

    def supprimer_eleve(self):
        """Demande confirmation puis supprime l'élève et ses paiements associés."""
        eleve = self.obtenir_eleve_selectionne()
        if eleve is None:
            return

        paiements = PaiementDAO.get_by_eleve(eleve[0])
        confirmation = QMessageBox.warning(
            self,
            "Confirmer la suppression",
            f"Supprimer définitivement {eleve[2]} {eleve[3]} ({eleve[1]}) ?\n\n"
            f"Les {len(paiements)} paiement(s) et leur historique seront également supprimés. "
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        try:
            EleveDAO.delete(eleve[0])
        except Exception as error:
            QMessageBox.critical(self, "Suppression impossible", str(error))
            return

        self.charger_donnees()
        QMessageBox.information(self, "Élève supprimé", f"{eleve[2]} {eleve[3]} a été supprimé.")

    def generer_facture(self, row=None):
        """Génère une facture depuis la ligne sélectionnée ou double-cliquée."""
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

    def obtenir_eleve_selectionne(self):
        """Retourne l'élève choisi dans le tableau, ou None si aucune ligne n'est sélectionnée."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Sélection nécessaire", "Sélectionnez une ligne élève.")
            return None
        eleve_id = int(self.table.item(selected_rows[0].row(), 0).text())
        return next((item for item in EleveDAO.get_all() if item[0] == eleve_id), None)

    def afficher_historique(self):
        """Ouvre une fenêtre qui liste les paiements de l'élève sélectionné."""
        eleve = self.obtenir_eleve_selectionne()
        if eleve is None:
            QMessageBox.warning(self, "Élève introuvable", "L'élève sélectionné n'existe plus.")
            return

        paiements = PaiementDAO.get_by_eleve(eleve[0])
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Historique - {eleve[2]} {eleve[3]}")
        dialog.resize(650, 350)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Élève : {eleve[2]} {eleve[3]} | Matricule : {eleve[1]}"))

        history_table = QTableWidget(0, 4)
        history_table.setHorizontalHeaderLabels(["Date", "Montant", "Mode", "Référence"])
        history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        total = Decimal("0")
        for paiement_id, montant, date_paiement, mode_paiement in paiements:
            row = history_table.rowCount()
            history_table.insertRow(row)
            history_table.setItem(row, 0, QTableWidgetItem(date_paiement))
            history_table.setItem(row, 1, QTableWidgetItem(self.format_montant(montant)))
            history_table.setItem(row, 2, QTableWidgetItem(mode_paiement))
            history_table.setItem(row, 3, QTableWidgetItem(f"PAY-{paiement_id:04d}"))
            total += Decimal(str(montant))
        layout.addWidget(history_table)
        layout.addWidget(QLabel(f"Total payé : {self.format_montant(total)}"))
        close_button = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_button.rejected.connect(dialog.reject)
        close_button.accepted.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec()

    def imprimer_recu(self):
        """Ouvre le dialogue d'impression pour le dernier paiement de l'élève."""
        eleve = self.obtenir_eleve_selectionne()
        if eleve is None:
            QMessageBox.warning(self, "Élève introuvable", "L'élève sélectionné n'existe plus.")
            return
        paiements = PaiementDAO.get_by_eleve(eleve[0])
        if not paiements:
            QMessageBox.information(self, "Aucun paiement", "Cet élève n'a aucun reçu à imprimer.")
            return

        paiement_id, montant, date_paiement, mode_paiement = paiements[0]
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        painter = QPainter(printer)
        try:
            painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            painter.drawText(QRect(500, 500, 7000, 500), "REÇU DE PAIEMENT - EDUPAIE")
            painter.setFont(QFont("Arial", 11))
            lines = [
                f"Référence : PAY-{paiement_id:04d}",
                f"Élève : {eleve[2]} {eleve[3]}",
                f"Matricule : {eleve[1]}",
                f"Classe : {eleve[4]}",
                f"Montant réglé : {self.format_montant(montant)}",
                f"Date : {date_paiement}",
                f"Mode de paiement : {mode_paiement}",
            ]
            for index, line in enumerate(lines, start=2):
                painter.drawText(700, 500 + index * 500, line)
        finally:
            painter.end()

    def ajouter_eleve(self):
        """Affiche le formulaire et enregistre un élève si ses champs sont remplis."""
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
        """Affiche le formulaire de versement; le DAO contrôle le montant avant l'insertion."""
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
    # Ce bloc ne s'exécute que lorsque ce fichier est lancé directement par Python.
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
