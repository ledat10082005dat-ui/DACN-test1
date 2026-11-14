import json
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import ConsultationSession, User
from app.routers.auth import get_current_user_optional, get_current_user
from app.pdf_generator import generate_pdf_report

router = APIRouter(prefix="/history", tags=["Consultation History & PDF Export"])

@router.get("/")
def get_user_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách các phiên tư vấn của sinh viên đã đăng nhập"""
    sessions = (
        db.query(ConsultationSession)
        .filter(ConsultationSession.user_id == current_user.id)
        .order_by(ConsultationSession.created_at.desc())
        .all()
    )
    result = []
    for s in sessions:
        top_majors = []
        if s.top_majors_json:
            try:
                top_majors = json.loads(s.top_majors_json)
            except Exception:
                pass
        result.append({
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at,
            "overview_analysis": s.overview_analysis,
            "top_majors": top_majors
        })
    return result


@router.get("/{session_id}")
def get_session_detail(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Xem chi tiết một phiên tư vấn"""
    session = db.query(ConsultationSession).filter(ConsultationSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên tư vấn!")

    top_majors = []
    if session.top_majors_json:
        try:
            top_majors = json.loads(session.top_majors_json)
        except Exception:
            pass

    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "overview_analysis": session.overview_analysis,
        "top_majors": top_majors,
        "profile": {
            "major_combinations": session.profile.major_combinations if session.profile else "",
            "academic_performance": session.profile.academic_performance if session.profile else "",
            "preferred_environment": session.profile.preferred_environment if session.profile else "",
            "preferred_locations": session.profile.preferred_locations if session.profile else "",
            "tuition_budget": session.profile.tuition_budget if session.profile else "",
            "top_priority": session.profile.top_priority if session.profile else ""
        } if session.profile else None
    }


@router.get("/{session_id}/export-pdf")
def export_consultation_pdf(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Xuất file PDF báo cáo kết quả tư vấn định hướng ngành học"""
    session = db.query(ConsultationSession).filter(ConsultationSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên tư vấn!")

    pdf_bytes = generate_pdf_report(session, user=current_user or session.user)

    filename = f"Bao_cao_dinh_huong_nganh_{session.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
