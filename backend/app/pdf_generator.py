import io
import json
from datetime import datetime

def generate_pdf_report(session, user=None) -> bytes:
    """
    Tạo file PDF báo cáo kết quả tư vấn chuyển ngành, phân tích Skill Gap & Lộ trình học.
    """
    buffer = io.BytesIO()
    
    candidate_name = user.full_name if user else "Ung vien / Nguoi chuyen nganh"
    created_date = session.created_at.strftime("%d/%m/%Y %H:%M") if session.created_at else datetime.now().strftime("%d/%m/%Y")
    
    job_roles = []
    raw_json = session.job_roles_json or session.top_majors_json
    if raw_json:
        try:
            job_roles = json.loads(raw_json)
        except Exception:
            job_roles = []

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        # Tiêu đề
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=10,
            alignment=1 # Center
        )
        story.append(Paragraph("BAO CAO PHAN TICH SKILL GAP & LO TRINH CHUYEN NGANH", title_style))
        story.append(Spacer(1, 8))

        # Thông tin ứng viên
        info_data = [
            ["Ho va ten:", candidate_name, "Ngay phan tich:", created_date],
            ["Ma ho so:", f"#{session.id}", "Dinh huong:", getattr(session.profile, 'target_career', 'Chuyen nganh') or 'Chuyen nganh']
        ]
        info_table = Table(info_data, colWidths=[90, 190, 100, 160])
        info_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#374151')),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 12))

        # Nhận xét tổng quan
        if session.overview_analysis:
            sub_title = Paragraph("<b>1. TONG QUAN HIEN TRANG & KY NANG SAN CO:</b>", styles['Heading2'])
            story.append(sub_title)
            story.append(Spacer(1, 4))
            clean_overview = session.overview_analysis.encode('ascii', 'ignore').decode('ascii')
            story.append(Paragraph(clean_overview or session.overview_analysis, styles['Normal']))
            story.append(Spacer(1, 12))

        # Bảng Vị trí việc làm & Khoảng trống kỹ năng
        sub_title2 = Paragraph("<b>2. TOP VI TRI CONG VIEC PHU HOP & SKILL GAP:</b>", styles['Heading2'])
        story.append(sub_title2)
        story.append(Spacer(1, 6))

        headers = ["Vi tri cong viec", "Tuong thich", "Skill Gap (Can hoc)", "Muc luong tham khao"]
        table_rows = [headers]
        for r in job_roles:
            title = (r.get("job_title") or r.get("major_name") or "").encode('ascii', 'ignore').decode('ascii')
            fit = f"{r.get('match_percentage', 0)}%"
            missing = ", ".join(r.get("missing_skills", [])[:3]).encode('ascii', 'ignore').decode('ascii')
            salary = (r.get("expected_salary") or r.get("starting_salary") or "").encode('ascii', 'ignore').decode('ascii')
            table_rows.append([title, fit, missing, salary])

        job_table = Table(table_rows, colWidths=[180, 70, 160, 130])
        job_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(job_table)
        story.append(Spacer(1, 15))

        # Lộ trình & Lời khuyên
        sub_title3 = Paragraph("<b>3. LOI KHUYEN TOI UU CV & DI PHONG VAN:</b>", styles['Heading2'])
        story.append(sub_title3)
        story.append(Spacer(1, 4))
        advice = (
            "- Xay dung Portfolio thuc chien voi it nhat 2 du an thuc te de bu dap viec thieu bang cap dung nganh.<br/>"
            "- Toi uu CV theo cau truc Functional Resume, dua ky nang va du an len dau.<br/>"
            "- Luon the hien thai do cau tien, san sang hoc hoi va chung minh Transferable Skills trong phuong phap phong van STAR."
        )
        story.append(Paragraph(advice, styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        # Fallback text format
        plain_text = f"=== BAO CAO CHUYEN NGANH #{session.id} ===\nUng vien: {candidate_name}\nNgay: {created_date}\n\n{session.overview_analysis}"
        return plain_text.encode('utf-8')
