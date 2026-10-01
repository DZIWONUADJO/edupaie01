import os
from fpdf import FPDF

class PDFService:
    @staticmethod
    def generer_recu(eleve_nom, eleve_prenom, classe, montant, mode_p, recu_no="REC-2026-001"):
        os.makedirs("edupaie/data/recu", exist_ok=True)
        filename = f"edupaie/data/recu/{recu_no}.pdf"
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "REÇU DE PAIEMENT - EDUPAIE", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"N° de Reçu : {recu_no}", ln=True)
        pdf.cell(0, 8, f"Élève : {eleve_nom} {eleve_prenom}", ln=True)
        pdf.cell(0, 8, f"Classe : {classe}", ln=True)
        pdf.cell(0, 8, f"Montant Réglé : {montant:,} FCFA", ln=True)
        pdf.cell(0, 8, f"Mode de Règlement : {mode_p}", ln=True)
        
        pdf.output(filename)
        return filename

