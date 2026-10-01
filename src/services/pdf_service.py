import os
from decimal import Decimal

class PDFService:
    @staticmethod
    def generer_recu(eleve_nom, eleve_prenom, classe, montant, mode_p, recu_no="REC-2026-001"):
        from fpdf import FPDF

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        receipt_dir = os.path.join(base_dir, "recus")
        os.makedirs(receipt_dir, exist_ok=True)
        filename = os.path.join(receipt_dir, f"{recu_no}.pdf")
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "REÇU DE PAIEMENT - EDUPAIE", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"N° de Reçu : {recu_no}", ln=True)
        pdf.cell(0, 8, f"Élève : {eleve_nom} {eleve_prenom}", ln=True)
        pdf.cell(0, 8, f"Classe : {classe}", ln=True)
        pdf.cell(0, 8, f"Montant Réglé : {Decimal(str(montant)):,.2f} FCFA", ln=True)
        pdf.cell(0, 8, f"Mode de Règlement : {mode_p}", ln=True)
        
        pdf.output(filename)
        return filename

    @staticmethod
    def generer_facture(matricule, eleve_nom, eleve_prenom, classe, total_du, total_paye, reste, dernier_paiement, facture_no):
        from fpdf import FPDF

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        receipt_dir = os.path.join(base_dir, "recus")
        os.makedirs(receipt_dir, exist_ok=True)
        filename = os.path.join(receipt_dir, f"{facture_no}.pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "FACTURE SCOLAIRE - EDUPAIE", ln=True, align="C")
        pdf.ln(8)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"N° de facture : {facture_no}", ln=True)
        pdf.cell(0, 8, f"Matricule : {matricule}", ln=True)
        pdf.cell(0, 8, f"Élève : {eleve_nom} {eleve_prenom}", ln=True)
        pdf.cell(0, 8, f"Classe : {classe}", ln=True)
        pdf.ln(6)
        pdf.cell(0, 8, f"Total dû : {Decimal(str(total_du)):,.2f} FCFA", ln=True)
        pdf.cell(0, 8, f"Total payé : {Decimal(str(total_paye)):,.2f} FCFA", ln=True)
        pdf.cell(0, 8, f"Reste : {Decimal(str(reste)):,.2f} FCFA", ln=True)
        if dernier_paiement:
            _, montant, date_paiement, mode_paiement = dernier_paiement
            pdf.ln(6)
            pdf.cell(0, 8, f"Dernier paiement : {Decimal(str(montant)):,.2f} FCFA", ln=True)
            pdf.cell(0, 8, f"Date : {date_paiement} - Mode : {mode_paiement}", ln=True)
        else:
            pdf.ln(6)
            pdf.cell(0, 8, "Aucun paiement enregistré", ln=True)

        pdf.output(filename)
        return filename

