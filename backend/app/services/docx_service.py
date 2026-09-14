import os
import re
from datetime import datetime
from app.config import settings

class DOCXService:
    def __init__(self):
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)

    def generate_draft_docx(self, draft_title: str, client_name: str, draft_text: str) -> str:
        """
        Generates a formatted DOCX document file for legal drafts.
        Uses python-docx with clean legal formatting (margins, alignment, bold titles).
        """
        filename = f"LegalIQ_Draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        file_path = os.path.join(settings.REPORTS_DIR, filename)

        try:
            from docx import Document
            from docx.shared import Inches, Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            doc = Document()
            
            # Header Title
            title_p = doc.add_paragraph()
            title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = title_p.add_run("LEGALIQ ARTIFICIAL INTELLIGENCE LEGAL PLATFORM\n")
            run.bold = True
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(30, 58, 138)

            sub_run = title_p.add_run(f"FORMAL LEGAL DRAFTING: {draft_title.upper()}\n")
            sub_run.bold = True
            sub_run.font.size = Pt(12)

            meta_p = doc.add_paragraph()
            meta_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            meta_run = meta_p.add_run(f"Client: {client_name} | Date: {datetime.now().strftime('%B %d, %Y')}")
            meta_run.font.size = Pt(9)
            meta_run.italic = True

            doc.add_paragraph("=" * 60)

            # Clean markdown symbols & format paragraphs
            paragraphs = draft_text.split("\n")
            for p_text in paragraphs:
                clean_text = re.sub(r'[\*#_`]', '', p_text).strip()
                if clean_text:
                    p = doc.add_paragraph()
                    p.paragraph_format.line_spacing = 1.15
                    p.paragraph_format.space_after = Pt(6)

                    # Center alignment for headings & titles
                    if any(header in clean_text for header in ["BEFORE THE COMPETENT", "LEGAL DRAFT TYPE:", "IN THE MATTER OF:", "VERSUS", "DATED:", "LOCATION:"]):
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_run = p.add_run(clean_text)
                        p_run.bold = True
                    else:
                        p.add_run(clean_text)

            doc.add_paragraph("\n" + "=" * 60)
            footer_p = doc.add_paragraph("Confidential Legal Document — Prepared via LegalIQ Multi-Agent Legal Engine")
            footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            footer_p.runs[0].font.size = Pt(8)
            footer_p.runs[0].font.italic = True

            doc.save(file_path)

        except Exception as e:
            # Fallback text saving if python-docx not available
            clean_draft = re.sub(r'[\*#_`]', '', draft_text)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"LEGALIQ FORMAL LEGAL DRAFTING: {draft_title}\n")
                f.write(f"Client: {client_name} | Date: {datetime.now().strftime('%B %d, %Y')}\n\n")
                f.write("=" * 60 + "\n\n")
                f.write(clean_draft)
                f.write("\n\n" + "=" * 60 + "\n")
                f.write("Confidential Legal Document — LegalIQ AI\n")

        return file_path

docx_service = DOCXService()
