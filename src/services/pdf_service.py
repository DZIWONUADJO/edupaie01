import os

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
        pdf.cell(0, 8, f"Montant Réglé : {montant:,} FCFA", ln=True)
        pdf.cell(0, 8, f"Mode de Règlement : {mode_p}", ln=True)
        
        pdf.output(filename)
        return filename

