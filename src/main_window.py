# -*- coding: utf-8 -*-
"""Fenetre principale EduPaie."""

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

BTN_MODIFIER  = "Modifier l\u2019\u00e9l\u00e8ve"
BTN_SUPPRIMER = "Supprimer l\u2019\u00e9l\u00e8ve"
LBL_ELEVES    = "\u00c9L\u00c8VES"
LBL_DU        = "TOTAL D\u00db"
LBL_PAYE      = "TOTAL PAY\u00c9"
LBL_RESTE     = "RESTE \u00c0 PAYER"
LBL_SUIVI     = "Suivi des \u00e9l\u00e8ves"
PLACEHOLDER   = "Rechercher un \u00e9l\u00e8ve..."
TITRE_PAGE    = "Vue d\u2019ensemble"
NOUVEAU_PAI   = "Nouveau paiement"
TITRE_APP     = "EduPaie - Gestion des Frais Scolaires"
SUBTITLE_APP  = "GESTION DES FRAIS SCOLAIRES"


class MainWindow(QMainWindow):

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
        self.setWindowTitle(TITRE_APP)
        self.resize(1180, 720)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(self.APP_STYLE)
        self.init_ui()
        self.charger_donnees()

    @staticmethod
    def charger_polices_systeme():
        for fp in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"):
            if os.path.exists(fp):
                QFontDatabase.addApplicationFont(fp)

    @staticmethod
    def format_montant(montant):
        return f"{Decimal(str(montant)):,.2f} FCFA"

    def init_ui(self):
        main_widget = QWidget()
        main_widget.setObjectName("appRoot")
        root_layout = QVBoxLayout(main_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Bandeau ---
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(62)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        brand = QLabel("EduPaie")
        brand.setObjectName("brand")
        top_layout.addWidget(brand)
        top_layout.addStretch()
        subtitle = QLabel(SUBTITLE_APP)
        subtitle.setObjectName("topBarSubtitle")
        top_layout.addWidget(subtitle)
        root_layout.addWidget(top_bar)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # --- Sidebar ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(205)
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(0, 16, 0, 16)
        sl.setSpacing(3)
        self.navigation_group = QButtonGroup(self)
        self.navigation_group.setExclusive(True)

        def heading(txt):
            h = QLabel(txt)
            h.setObjectName("sidebarHeading")
            return h

        sl.addWidget(heading("ACTIONS"))
        sl.addWidget(self.creer_bouton_menu("Vue d\u2019ensemble", self.afficher_tous_les_eleves, checked=True))
        sl.addWidget(self.creer_bouton_menu("Nouvel \u00e9l\u00e8ve", self.ajouter_eleve))

        sl.addWidget(heading("PAIEMENTS"))
        sl.addWidget(self.creer_bouton_menu("Historique paiements", self.afficher_historique))
        sl.addWidget(self.creer_bouton_menu("Imprimer re\u00e7u", self.imprimer_recu))

        sl.addWidget(heading("DOCUMENTS"))
        sl.addWidget(self.creer_bouton_menu("Facture PDF", self.generer_facture))

        sl.addWidget(heading("DONN\u00c9ES"))
        sl.addWidget(self.creer_bouton_menu("Sauvegarder", self.sauvegarder_base))
        sl.addWidget(self.creer_bouton_menu("Restaurer", self.restaurer_base))

        sl.addWidget(heading("GESTION"))
        # ---- BOUTON MODIFIER ----
        sl.addWidget(self.creer_bouton_menu(BTN_MODIFIER, self.modifier_eleve))
        # ---- BOUTON SUPPRIMER ----
        btn_del = QPushButton(BTN_SUPPRIMER)
        btn_del.setObjectName("dangerButton")
        btn_del.clicked.connect(self.supprimer_eleve)
        sl.addWidget(btn_del)

        sl.addStretch()
        body_layout.addWidget(sidebar)

        # --- Zone centrale ---
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(26, 22, 26, 24)
        cl.setSpacing(16)

        title_row = QHBoxLayout()
        title = QLabel(TITRE_PAGE)
        title.setObjectName("pageTitle")
        title_row.addWidget(title)
        title_row.addStretch()
        btn_paiement = QPushButton(NOUVEAU_PAI)
        btn_paiement.setObjectName("primaryButton")
        btn_paiement.clicked.connect(self.ajouter_paiement)
        title_row.addWidget(btn_paiement)
        cl.addLayout(title_row)

        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(PLACEHOLDER)
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.charger_donnees)
        filter_row.addWidget(self.search_input)
        lbl_c = QLabel("Classe")
        lbl_c.setObjectName("mutedText")
        filter_row.addWidget(lbl_c)
        self.class_filter = QComboBox()
        self.class_filter.setFixedWidth(160)
        self.class_filter.addItem("Toutes les classes", "")
        self.class_filter.currentIndexChanged.connect(self.charger_donnees)
        filter_row.addWidget(self.class_filter)
        lbl_s = QLabel("Statut")
        lbl_s.setObjectName("mutedText")
        filter_row.addWidget(lbl_s)
        self.status_filter = QComboBox()
        self.status_filter.setFixedWidth(150)
        self.status_filter.addItem("Tous les statuts", "")
        for s in ("En retard", "En cours", "Sold\u00e9", "Cr\u00e9dit"):
            self.status_filter.addItem(s, s)
        self.status_filter.currentIndexChanged.connect(self.charger_donnees)
        filter_row.addWidget(self.status_filter)
        filter_row.addStretch()
        cl.addLayout(filter_row)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(12)
        metrics.setVerticalSpacing(12)
        self.total_eleves_label = self.creer_carte_indicateur(metrics, 0, 0, LBL_ELEVES)
        self.total_du_label     = self.creer_carte_indicateur(metrics, 0, 1, LBL_DU)
        self.total_paye_label   = self.creer_carte_indicateur(metrics, 0, 2, LBL_PAYE)
        self.total_reste_label  = self.creer_carte_indicateur(metrics, 0, 3, LBL_RESTE)
        cl.addLayout(metrics)

        th = QHBoxLayout()
        st = QLabel(LBL_SUIVI)
        st.setObjectName("sectionTitle")
        th.addWidget(st)
        th.addStretch()
        cl.addLayout(th)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Matricule", "Nom", "Pr\u00e9nom", "Classe", "D\u00fb", "Pay\u00e9", "Reste", "Statut"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(0, True)
        self.table.cellDoubleClicked.connect(lambda row, _col: self.generer_facture(row))
        cl.addWidget(self.table)

        body_layout.addWidget(content, 1)
        root_layout.addWidget(body, 1)
        self.setCentralWidget(main_widget)

    # ------------------------------------------------------------------
    def creer_bouton_menu(self, texte, action, checked=False):
        btn = QPushButton(texte)
        btn.setObjectName("navButton")
        btn.setCheckable(True)
        btn.setChecked(checked)
        self.navigation_group.addButton(btn)
        btn.clicked.connect(action)
        return btn

    def creer_carte_indicateur(self, grid, row, col, titre):
        card = QFrame()
        card.setObjectName("metricCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 14)
        lay.setSpacing(7)
        t = QLabel(titre)
        t.setObjectName("metricTitle")
        v = QLabel("0")
        v.setObjectName("metricValue")
        lay.addWidget(t)
        lay.addWidget(v)
        grid.addWidget(card, row, col)
        return v

    # ------------------------------------------------------------------
    def afficher_tous_les_eleves(self):
        for w in (self.search_input, self.class_filter, self.status_filter):
            w.blockSignals(True)
        self.search_input.clear()
        self.class_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        for w in (self.search_input, self.class_filter, self.status_filter):
            w.blockSignals(False)
        self.charger_donnees()

    def charger_donnees(self):
        eleves = EleveService.obtenir_liste_eleves_avec_solde()
        filtre = self.search_input.text().lower()

        classe_sel = self.class_filter.currentData()
        classes = sorted({e["classe"] for e in eleves}, key=str.casefold)
        if [self.class_filter.itemText(i) for i in range(1, self.class_filter.count())] != classes:
            self.class_filter.blockSignals(True)
            self.class_filter.clear()
            self.class_filter.addItem("Toutes les classes", "")
            for c in classes:
                self.class_filter.addItem(c, c)
            idx = self.class_filter.findData(classe_sel)
            self.class_filter.setCurrentIndex(max(0, idx))
            self.class_filter.blockSignals(False)

        classe_sel = self.class_filter.currentData()
        statut_sel = self.status_filter.currentData()

        total_du   = sum(e["frais"] for e in eleves)
        total_paye = sum(e["paye"]  for e in eleves)
        self.total_eleves_label.setText(str(len(eleves)))
        self.total_du_label.setText(self.format_montant(total_du))
        self.total_paye_label.setText(self.format_montant(total_paye))
        self.total_reste_label.setText(self.format_montant(total_du - total_paye))

        self.table.setRowCount(0)
        for e in eleves:
            texte = f"{e['nom']} {e['prenom']} {e['matricule']}".lower()
            if filtre and filtre not in texte:
                continue
            if classe_sel and e["classe"] != classe_sel:
                continue
            if statut_sel and e["statut"] != statut_sel:
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
            si = QTableWidgetItem(e["statut"])
            si.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            colors = {
                "En retard": ("#8a5700", "#fff1d2"),
                "En cours":  ("#245b86", "#e8f2fa"),
                "Sold\u00e9":  ("#08784e", "#e5f3eb"),
                "Cr\u00e9dit": ("#176c70", "#e4f3f2"),
            }
            fg, bg = colors.get(e["statut"], ("#53645b", "#f1f4f2"))
            si.setForeground(QColor(fg))
            si.setBackground(QColor(bg))
            self.table.setItem(row, 8, si)

    # ------------------------------------------------------------------
    def modifier_eleve(self):
        """Ouvre un formulaire prerempli et enregistre les modifications."""
        eleve = self.obtenir_eleve_selectionne()
        if eleve is None:
            return
        # eleve = (id, matricule, nom, prenom, classe, frais_scolarite)
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier un \u00e9l\u00e8ve")
        form = QFormLayout(dialog)

        lbl_mat = QLabel(eleve[1])
        lbl_mat.setObjectName("mutedText")
        nom    = QLineEdit(eleve[2])
        prenom = QLineEdit(eleve[3])
        classe = QLineEdit(eleve[4])
        frais  = QDoubleSpinBox()
        frais.setRange(0, 1_000_000_000)
        frais.setDecimals(2)
        frais.setSuffix(" FCFA")
        frais.setValue(float(eleve[5]))

        form.addRow("Matricule :", lbl_mat)
        form.addRow("Nom :", nom)
        form.addRow("Pr\u00e9nom :", prenom)
        form.addRow("Classe :", classe)
        form.addRow("Frais de scolarit\u00e9 :", frais)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        form.addRow(btns)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        vals = [nom.text().strip(), prenom.text().strip(), classe.text().strip()]
        if not all(vals):
            QMessageBox.warning(self, "Champs manquants", "Nom, pr\u00e9nom et classe sont obligatoires.")
            return
        try:
            EleveDAO.update(eleve[0], vals[0], vals[1], vals[2], frais.value())
        except Exception as err:
            QMessageBox.critical(self, "Modification impossible", str(err))
            return
        self.charger_donnees()
        QMessageBox.information(self, "\u00c9l\u00e8ve modifi\u00e9", f"{vals[0]} {vals[1]} a \u00e9t\u00e9 mis \u00e0 jour.")

    # ------------------------------------------------------------------
    def supprimer_eleve(self):
        eleve = self.obtenir_eleve_selectionne()
        if eleve is None:
            return
        paiements = PaiementDAO.get_by_eleve(eleve[0])
        rep = QMessageBox.warning(
            self, "Confirmer la suppression",
            f"Supprimer {eleve[2]} {eleve[3]} ({eleve[1]}) ?\n\n"
            f"Les {len(paiements)} paiement(s) seront aussi supprim\u00e9s. Action irr\u00e9versible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if rep != QMessageBox.StandardButton.Yes:
            return
        try:
            EleveDAO.delete(eleve[0])
        except Exception as err:
            QMessageBox.critical(self, "Suppression impossible", str(err))
            return
        self.charger_donnees()
        QMessageBox.information(self, "\u00c9l\u00e8ve supprim\u00e9", f"{eleve[2]} {eleve[3]} a \u00e9t\u00e9 supprim\u00e9.")

    # ------------------------------------------------------------------
    def generer_facture(self, row=None):
        if row is None:
            rows = self.table.selectionModel().selectedRows()
            if not rows:
                QMessageBox.information(self, "S\u00e9lection n\u00e9cessaire", "S\u00e9lectionnez un \u00e9l\u00e8ve.")
                return
            row = rows[0].row()
        eleve_id = int(self.table.item(row, 0).text())
        donnees  = next((e for e in EleveService.obtenir_liste_eleves_avec_solde() if e["id"] == eleve_id), None)
        eleve    = next((e for e in EleveDAO.get_all() if e[0] == eleve_id), None)
        if eleve is None or donnees is None:
            QMessageBox.warning(self, "Introuvable", "\u00c9l\u00e8ve introuvable.")
            return
        paiements        = PaiementDAO.get_by_eleve(eleve_id)
        dernier_paiement = paiements[0] if paiements else None
        facture_no       = f"FAC-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{eleve_id:04d}"
        try:
            filename = PDFService.generer_facture(
                eleve[1], eleve[2], eleve[3], eleve[4],
                donnees["frais"], donnees["paye"], donnees["reste"],
                dernier_paiement, facture_no,
            )
        except Exception as err:
            QMessageBox.critical(self, "Erreur PDF", str(err))
            return
        QMessageBox.information(self, "Facture g\u00e9n\u00e9r\u00e9e", f"Fichier cr\u00e9\u00e9 :\n{filename}")

    # ------------------------------------------------------------------
    def obtenir_eleve_selectionne(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "S\u00e9lection n\u00e9cessaire", "S\u00e9lectionnez un \u00e9l\u00e8ve.")
            return None
        eleve_id = int(self.table.item(rows[0].row(), 0).text())
        return next((e for e in EleveDAO.get_all() if e[0] == eleve_id), None)

    # ------------------------------------------------------------------
    def afficher_historique(self):
        eleve = self.obtenir_eleve_selectionne()
        if eleve is None:
            return
        paiements = PaiementDAO.get_by_eleve(eleve[0])
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Historique - {eleve[2]} {eleve[3]}")
        dialog.resize(650, 350)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"\u00c9l\u00e8ve : {eleve[2]} {eleve[3]}  |  Matricule : {eleve[1]}"))
        tbl = QTableWidget(0, 4)
        tbl.setHorizontalHeaderLabels(["Date", "Montant", "Mode", "R\u00e9f\u00e9rence"])
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        total = Decimal("0")
        for pid, montant, date_p, mode_p in paiements:
            r = tbl.rowCount()
            tbl.insertRow(r)
            tbl.setItem(r, 0, QTableWidgetItem(date_p))
            tbl.setItem(r, 1, QTableWidgetItem(self.format_montant(montant)))
            tbl.setItem(r, 2, QTableWidgetItem(mode_p))
            tbl.setItem(r, 3, QTableWidgetItem(f"PAY-{pid:04d}"))
            total += Decimal(str(montant))
        layout.addWidget(tbl)
        layout.addWidget(QLabel(f"Total pay\u00e9 : {self.format_montant(total)}"))
        cb = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        cb.rejected.connect(dialog.reject)
        cb.accepted.connect(dialog.accept)
        layout.addWidget(cb)
        dialog.exec()

    # ------------------------------------------------------------------
    def imprimer_recu(self):
        eleve = self.obtenir_eleve_selectionne()
        if eleve is None:
            return
        paiements = PaiementDAO.get_by_eleve(eleve[0])
        if not paiements:
            QMessageBox.information(self, "Aucun paiement", "Cet \u00e9l\u00e8ve n\u2019a aucun re\u00e7u.")
            return
        pid, montant, date_p, mode_p = paiements[0]
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dlg = QPrintDialog(printer, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        painter = QPainter(printer)
        try:
            painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            painter.drawText(QRect(500, 500, 7000, 500), "RECU DE PAIEMENT - EDUPAIE")
            painter.setFont(QFont("Arial", 11))
            lines = [
                f"Reference : PAY-{pid:04d}",
                f"Eleve : {eleve[2]} {eleve[3]}",
                f"Matricule : {eleve[1]}",
                f"Classe : {eleve[4]}",
                f"Montant : {self.format_montant(montant)}",
                f"Date : {date_p}",
                f"Mode : {mode_p}",
            ]
            for i, line in enumerate(lines, start=2):
                painter.drawText(700, 500 + i * 500, line)
        finally:
            painter.end()

    # ------------------------------------------------------------------
    def ajouter_eleve(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un \u00e9l\u00e8ve")
        form = QFormLayout(dialog)
        matricule = QLineEdit()
        nom       = QLineEdit()
        prenom    = QLineEdit()
        classe    = QLineEdit()
        frais     = QDoubleSpinBox()
        frais.setRange(0, 1_000_000_000)
        frais.setDecimals(2)
        frais.setSuffix(" FCFA")
        form.addRow("Matricule :", matricule)
        form.addRow("Nom :", nom)
        form.addRow("Pr\u00e9nom :", prenom)
        form.addRow("Classe :", classe)
        form.addRow("Frais de scolarit\u00e9 :", frais)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        form.addRow(btns)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        vals = [matricule.text().strip(), nom.text().strip(), prenom.text().strip(), classe.text().strip()]
        if not all(vals):
            QMessageBox.warning(self, "Champs manquants", "Tous les champs sont obligatoires.")
            return
        try:
            EleveDAO.create(*vals, frais.value())
        except Exception as err:
            QMessageBox.critical(self, "Ajout impossible", str(err))
            return
        self.charger_donnees()

    # ------------------------------------------------------------------
    def ajouter_paiement(self):
        eleves = EleveDAO.get_all()
        if not eleves:
            QMessageBox.information(self, "Aucun \u00e9l\u00e8ve", "Ajoutez d\u2019abord un \u00e9l\u00e8ve.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Enregistrer un paiement")
        form = QFormLayout(dialog)
        cb_eleve = QComboBox()
        for e in eleves:
            cb_eleve.addItem(f"{e[1]} - {e[2]} {e[3]}", e[0])
        montant = QDoubleSpinBox()
        montant.setRange(0.01, 1_000_000_000)
        montant.setDecimals(2)
        montant.setSuffix(" FCFA")
        date_p = QDateEdit(QDate.currentDate())
        date_p.setCalendarPopup(True)
        mode = QComboBox()
        mode.addItems(["Esp\u00e8ces", "Virement", "Ch\u00e8que", "Mobile Money"])
        form.addRow("\u00c9l\u00e8ve :", cb_eleve)
        form.addRow("Montant :", montant)
        form.addRow("Date :", date_p)
        form.addRow("Mode de paiement :", mode)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        form.addRow(btns)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            PaiementDAO.add_paiement(
                cb_eleve.currentData(),
                montant.value(),
                date_p.date().toString("yyyy-MM-dd"),
                mode.currentText(),
            )
        except Exception as err:
            QMessageBox.critical(self, "Paiement impossible", str(err))
            return
        self.charger_donnees()

    # ------------------------------------------------------------------
    def sauvegarder_base(self):
        default = os.path.join(
            os.path.dirname(DB_PATH),
            f"edupaie_sauvegarde_{datetime.now().strftime('%Y%m%d-%H%M%S')}.db",
        )
        dest, _ = QFileDialog.getSaveFileName(self, "Sauvegarder", default, "Base SQLite (*.db)")
        if not dest:
            return
        if not dest.lower().endswith(".db"):
            dest += ".db"
        try:
            path = create_backup(dest)
        except Exception as err:
            QMessageBox.critical(self, "Sauvegarde impossible", str(err))
            return
        QMessageBox.information(self, "Sauvegarde OK", f"Copie : {path}")

    def restaurer_base(self):
        src, _ = QFileDialog.getOpenFileName(
            self, "Choisir une sauvegarde", os.path.dirname(DB_PATH), "Base SQLite (*.db)"
        )
        if not src:
            return
        rep = QMessageBox.question(
            self, "Confirmer",
            "La restauration remplacera les donn\u00e9es actuelles. Continuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if rep != QMessageBox.StandardButton.Yes:
            return
        try:
            safety = restore_backup(src)
            init_db()
            self.charger_donnees()
        except Exception as err:
            QMessageBox.critical(self, "Restauration impossible", str(err))
            return
        QMessageBox.information(self, "Restauration OK", f"Copie de s\u00e9curit\u00e9 : {safety}")


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
