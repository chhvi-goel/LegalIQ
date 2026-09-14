import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
from app.config import settings

class PDFService:
    def generate_legal_report(
        self,
        user_name: str,
        query: str,
        response_text: str,
        citations: list,
        action_steps: list,
        report_type: str = "citizen_legal_advice"
    ) -> str:
        filename = f"LegalIQ_Report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(settings.REPORT_DIR, filename)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=12
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
            spaceAfter=10
        )

        elements = []

        # Header Title
        report_title = "LegalIQ — AI Legal Intelligence Consultation Report" if report_type == "citizen_legal_advice" else "LegalIQ — Research & Precedent Analysis Brief"
        elements.append(Paragraph(report_title, title_style))
        elements.append(Paragraph(f"<b>Prepared for:</b> {user_name} | <b>Date:</b> {datetime.utcnow().strftime('%B %d, %Y')}", body_style))
        elements.append(Spacer(1, 12))

        # User Query Section
        elements.append(Paragraph("<b>1. Subject / Query:</b>", subtitle_style))
        elements.append(Paragraph(query, body_style))
        elements.append(Spacer(1, 10))

        # Legal Guidance Section
        elements.append(Paragraph("<b>2. AI Legal Guidance & Reasoning:</b>", subtitle_style))
        cleaned_text = response_text.replace("#", "").replace("*", "")
        elements.append(Paragraph(cleaned_text[:1200] + ("..." if len(cleaned_text) > 1200 else ""), body_style))
        elements.append(Spacer(1, 10))

        # Citations Table
        if citations:
            elements.append(Paragraph("<b>3. Validated Legal Citations & Precedents:</b>", subtitle_style))
            table_data = [["No.", "Act / Court", "Provision", "Relevance"]]
            for idx, c in enumerate(citations[:5], 1):
                table_data.append([
                    str(idx),
                    str(c.get("act_or_court", "")),
                    str(c.get("section_or_year", "")),
                    f"{int(c.get('relevance_score', 0.8) * 100)}%"
                ])
            t = Table(table_data, colWidths=[30, 180, 180, 70])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0284c7")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 12))

        # Action Steps if Citizen
        if action_steps:
            elements.append(Paragraph("<b>4. Recommended Legal Action Steps:</b>", subtitle_style))
            for step in action_steps:
                step_str = f"<b>Step {step.get('step_number')}: {step.get('title')}</b> - {step.get('description')}"
                elements.append(Paragraph(step_str, body_style))
            elements.append(Spacer(1, 10))

        # Disclaimer
        elements.append(Paragraph("<i>Disclaimer: LegalIQ is an AI Legal Intelligence Assistant. This report is for informational purposes and does not constitute a formal attorney-client relationship.</i>", body_style))

        doc.build(elements)
        return file_path

pdf_service = PDFService()
