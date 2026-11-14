from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

# ===============================
# SCHEMAS FOR CAREER TRANSITION 4-STEP FORM
# ===============================

class TargetGroupStep(BaseModel):
    user_group: str = Field(..., description="Sinh viên năm cuối / Mới tốt nghiệp | Đang thất nghiệp / Tìm việc gấp | Đang đi làm muốn chuyển ngành (Career Switcher)")
    current_education_major: str = Field(..., description="Trình độ học vấn & Chuyên ngành hiện tại (VD: Đại học - Ngành Kế toán)")

class SkillsetStep(BaseModel):
    known_skills: List[str] = Field(..., description="Các kỹ năng / công cụ đã biết: Tiếng Anh, Excel, Bán hàng, Python, Photoshop...")
    custom_skills: Optional[str] = Field(None, description="Kỹ năng tự nhập thêm nếu có")
    experience_years: str = Field(..., description="Số năm kinh nghiệm: Chưa có / Mới ra trường | Dưới 1 năm | 1 - 3 năm | Trên 3 năm")

class CareerExpectationsStep(BaseModel):
    target_career: str = Field(..., description="Hướng đi đang quan tâm: CNTT, Digital Marketing, Chăm sóc khách hàng, Phân tích dữ liệu...")
    expected_salary: str = Field(..., description="Mức lương mong muốn / tháng: 8 - 12 triệu, 12 - 18 triệu, 18 - 25 triệu, Trên 25 triệu")
    learning_time: str = Field(..., description="Thời gian sẵn sàng đầu tư học: Học cấp tốc 1-3 tháng, 3-6 tháng, Vừa học vừa làm...")

class PriorityGoalStep(BaseModel):
    primary_goal: str = Field(..., description="Cần việc làm có thu nhập ngay lập tức | Cần lộ trình thăng tiến long-term chấp nhận Fresher/Intern")

class CareerFormSubmit(BaseModel):
    step1_target: Optional[TargetGroupStep] = None
    step2_skillset: Optional[SkillsetStep] = None
    step3_expectations: Optional[CareerExpectationsStep] = None
    step4_priority: Optional[PriorityGoalStep] = None
    # Hỗ trợ backward compatibility nếu có
    step1_academic: Optional[Any] = None
    step2_personality: Optional[Any] = None
    step3_preferences: Optional[Any] = None
    step4_expectations: Optional[Any] = None

# Alias
StudentFormSubmit = CareerFormSubmit

# ===============================
# SCHEMAS FOR CONSULTATION & CHAT
# ===============================

class JobRoleItem(BaseModel):
    job_title: str
    match_percentage: int
    reason: str
    transferable_skills: List[str] = Field(default_factory=list, description="Kỹ năng chuyển đổi được từ ngành cũ")
    missing_skills: List[str] = Field(default_factory=list, description="Khoảng trống kỹ năng cần học thêm (Skill Gap)")
    roadmap_summary: str = Field(default="", description="Tóm tắt lộ trình học")
    expected_salary: str = Field(default="", description="Mức lương tuyển dụng thị trường")
    suitable_companies: List[str] = Field(default_factory=list, description="Các loại doanh nghiệp tuyển dụng")

class FormAnalysisResponse(BaseModel):
    session_id: int
    profile_id: int
    overview_text: str
    job_roles: List[JobRoleItem]
    top_majors: Optional[List[Any]] = None  # Giữ cho backward compatibility
    created_at: datetime

class ChatMessageInput(BaseModel):
    session_id: int
    message: str
    mode: str = Field("skill_gap", description="skill_gap | roadmap | market_trend | roleplay")
    api_key: Optional[str] = None

class ChatMessageOutput(BaseModel):
    id: int
    role: str
    content: str
    mode: str
    created_at: datetime

# ===============================
# SCHEMAS FOR AUTH
# ===============================

class UserRegister(BaseModel):
    email: str
    full_name: str
    password: str
    role: Optional[str] = "student"

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime

# ===============================
# SCHEMAS FOR ADMIN DASHBOARD
# ===============================

class ChartDataPoint(BaseModel):
    name: str
    value: int

class AdminDashboardStats(BaseModel):
    total_consultations: int
    total_students: int
    user_groups: List[ChartDataPoint]
    top_known_skills: List[ChartDataPoint]
    popular_target_careers: List[ChartDataPoint]
    learning_time_distribution: List[ChartDataPoint]
    salary_expectations: List[ChartDataPoint]
    top_recommended_roles: List[ChartDataPoint]
