import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_patient_pdf(patient_id, doctor_id, prediction_data, patient_vitals, doctor_notes, output_path):
    """
    Generate a professional clinical health report in PDF.
    
    :param patient_id: Username of the patient
    :param doctor_id: Username of the doctor who performed the analysis
    :param prediction_data: Result from ml/predict.py
    :param patient_vitals: Dictionary of the 17 vitals
    :param doctor_notes: Text note from the doctor
    :param output_path: Where to save the PDF
    :return: output_path
    """
    # Ensure target directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom premium styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=12,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )
    
    bold_style = ParagraphStyle(
        'BoldText',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    recommendation_style = ParagraphStyle(
        'RecText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    story = []
    
    # Header Banner
    story.append(Paragraph("HealthChain AI Clinical Report", title_style))
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Secure Electronic Health Record (EHR) System  |  Generated: {timestamp_str}", subtitle_style))
    story.append(Spacer(1, 5))
    
    # Section: Diagnostic Summary
    story.append(Paragraph("1. Diagnostic Summary", h1_style))
    
    summary_data = [
        [
            Paragraph("Patient ID:", bold_style), Paragraph(str(patient_id), body_style),
            Paragraph("Doctor ID:", bold_style), Paragraph(str(doctor_id), body_style)
        ],
        [
            Paragraph("AI Prediction:", bold_style), Paragraph(f"<b>{prediction_data['prediction']}</b>", body_style),
            Paragraph("Risk Level:", bold_style), Paragraph(f"<b>{prediction_data['risk_level']}</b>", body_style)
        ],
        [
            Paragraph("Confidence Score:", bold_style), Paragraph(f"{prediction_data['confidence_score']:.1%}", body_style),
            Paragraph("Blockchain Status:", bold_style), Paragraph("Metadata Anchored on Ledger", body_style)
        ]
    ]
    
    summary_table = Table(summary_data, colWidths=[120, 140, 120, 140])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))
    
    # Section: Patient Clinical Vitals
    story.append(Paragraph("2. Patient Clinical Vitals", h1_style))
    
    # Grid of vitals
    vitals_data = []
    vitals_keys = list(patient_vitals.keys())
    imputed_features = prediction_data.get('imputed_features', [])
    
    # Format vitals into 2 columns
    for i in range(0, len(vitals_keys), 2):
        k1 = vitals_keys[i]
        v1 = patient_vitals[k1]
        k1_label = k1.replace("_", " ").title()
        if k1 in imputed_features:
            k1_label += " [Est.]"
        
        # Binary flag labels
        if k1 in ["Smoking", "Alcohol", "Family History"]:
            v1_str = "Yes" if int(v1) == 1 else "No"
        elif k1 == "Gender":
            v1_str = str(v1)
        else:
            v1_str = f"{v1:.2f}" if isinstance(v1, float) else str(v1)
            
        if i + 1 < len(vitals_keys):
            k2 = vitals_keys[i+1]
            v2 = patient_vitals[k2]
            k2_label = k2.replace("_", " ").title()
            if k2 in imputed_features:
                k2_label += " [Est.]"
            
            if k2 in ["Smoking", "Alcohol", "Family History"]:
                v2_str = "Yes" if int(v2) == 1 else "No"
            elif k2 == "Gender":
                v2_str = str(v2)
            else:
                v2_str = f"{v2:.2f}" if isinstance(v2, float) else str(v2)
                
            vitals_data.append([
                Paragraph(k1_label, bold_style), Paragraph(v1_str, body_style),
                Paragraph(k2_label, bold_style), Paragraph(v2_str, body_style)
            ])
        else:
            vitals_data.append([
                Paragraph(k1_label, bold_style), Paragraph(v1_str, body_style),
                Paragraph("", body_style), Paragraph("", body_style)
            ])
            
    vitals_table = Table(vitals_data, colWidths=[130, 130, 130, 130])
    vitals_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(vitals_table)
    story.append(Spacer(1, 10))
    
    # Section: Recommendations
    story.append(Paragraph("3. Clinical Recommendations", h1_style))
    from ml.recommendations import get_recommendations
    recs = get_recommendations(prediction_data['prediction'])
    for idx, rec in enumerate(recs):
        story.append(Paragraph(f"• {rec}", recommendation_style))
        
    story.append(Spacer(1, 8))
    
    # Section: Physician Notes
    if doctor_notes:
        story.append(Paragraph("4. Physician Notes & Observations", h1_style))
        clean_notes = str(doctor_notes).replace("\n", "<br/>")
        notes_table = Table([[Paragraph(clean_notes, body_style)]], colWidths=[520])
        notes_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF3C7')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#F59E0B')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(notes_table)
        
    doc.build(story)
    return output_path
