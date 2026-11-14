import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StudentProfile, ConsultationSession, User
from app.schemas import CareerFormSubmit, FormAnalysisResponse, JobRoleItem
from app.routers.auth import get_current_user_optional
from app.gemini_service import generate_initial_analysis

router = APIRouter(prefix="/profile", tags=["Career Transition Profile & Form 4 Steps"])

@router.post("/submit", response_model=FormAnalysisResponse)
async def submit_career_form(
    form_data: CareerFormSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Tiếp nhận dữ liệu khảo sát 4 bước từ người tìm việc / chuyển ngành:
    1. Lưu thông tin hồ sơ kỹ năng & hiện trạng vào CSDL
    2. Gọi AI/Gemini để phân tích Skill Gap & đề xuất Vị trí việc làm (Job Roles) + Lộ trình học (Roadmap)
    3. Tạo phiên tư vấn mới (ConsultationSession) và trả kết quả hiển thị cho UI ban đầu
    """
    raw_dict = form_data.model_dump()
    raw_json_str = json.dumps(raw_dict, ensure_ascii=False)

    # 1. Trích xuất dữ liệu Form 4 bước mới
    if form_data.step1_target and form_data.step2_skillset:
        user_group = form_data.step1_target.user_group
        current_education_major = form_data.step1_target.current_education_major
        skills_list = form_data.step2_skillset.known_skills or []
        if form_data.step2_skillset.custom_skills:
            skills_list.append(form_data.step2_skillset.custom_skills.strip())
        known_skills = ", ".join(skills_list)
        experience_years = form_data.step2_skillset.experience_years
        target_career = form_data.step3_expectations.target_career if form_data.step3_expectations else "Chuyển ngành"
        expected_salary = form_data.step3_expectations.expected_salary if form_data.step3_expectations else ""
        learning_time = form_data.step3_expectations.learning_time if form_data.step3_expectations else ""
        primary_goal = form_data.step4_priority.primary_goal if form_data.step4_priority else ""
        session_title = f"Chuyển sang: {target_career} ({user_group})"
    else:
        # Fallback dữ liệu cũ nếu có
        user_group = "Sinh viên chuẩn bị ra trường"
        current_education_major = "Đại học"
        known_skills = "Kỹ năng nền tảng"
        experience_years = "Mới ra trường"
        target_career = "Công nghệ thông tin"
        expected_salary = "10 - 15 triệu"
        learning_time = "3 - 6 tháng"
        primary_goal = "Cần việc làm ngay"
        session_title = "Định hướng nghề nghiệp"

    # Lưu hồ sơ
    profile = StudentProfile(
        user_id=current_user.id if current_user else None,
        user_group=user_group,
        current_education_major=current_education_major,
        known_skills=known_skills,
        experience_years=experience_years,
        target_career=target_career,
        expected_salary=expected_salary,
        learning_time=learning_time,
        primary_goal=primary_goal,
        raw_json=raw_json_str
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # 2. Sinh kết quả phân tích Vị trí việc làm & Khoảng trống kỹ năng (Skill Gap)
    analysis_result = await generate_initial_analysis(raw_dict)
    
    job_roles = analysis_result.get("job_roles", [])
    overview_text = analysis_result.get("overview_text", "")

    # 3. Tạo phiên tư vấn và lưu vào DB
    session = ConsultationSession(
        user_id=current_user.id if current_user else None,
        profile_id=profile.id,
        title=session_title,
        job_roles_json=json.dumps(job_roles, ensure_ascii=False),
        top_majors_json=json.dumps(job_roles, ensure_ascii=False), # tương thích
        overview_analysis=overview_text
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Đóng gói response
    job_role_items = [JobRoleItem(**item) for item in job_roles]

    return FormAnalysisResponse(
        session_id=session.id,
        profile_id=profile.id,
        overview_text=overview_text,
        job_roles=job_role_items,
        top_majors=[],
        created_at=session.created_at
    )
