import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="student")  # 'student' hoặc 'admin'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    profiles = relationship("StudentProfile", back_populates="user", cascade="all, delete-orphan")
    consultations = relationship("ConsultationSession", back_populates="user", cascade="all, delete-orphan")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Có thể ẩn danh hoặc đăng nhập
    
    # Bước 1: Phân loại đối tượng & Hiện trạng (Mới)
    user_group = Column(String(255), nullable=True)  # "Sinh viên năm cuối / Mới tốt nghiệp", "Đang thất nghiệp...", "Career Switcher"
    current_education_major = Column(String(255), nullable=True)  # "Đại học - Ngành Kế toán"

    # Bước 2: Hồ sơ kỹ năng & Kinh nghiệm (Mới)
    known_skills = Column(Text, nullable=True)  # "Tiếng Anh giao tiếp, Excel, Bán hàng..."
    experience_years = Column(String(100), nullable=True)  # "Chưa có kinh nghiệm", "1 - 3 năm"...

    # Bước 3: Kỳ vọng nghề nghiệp mới (Mới)
    target_career = Column(String(255), nullable=True)  # "Công nghệ thông tin", "Phân tích dữ liệu"...
    expected_salary = Column(String(100), nullable=True)  # "8 - 12 triệu", "12 - 18 triệu"...
    learning_time = Column(String(100), nullable=True)  # "Học cấp tốc 1-3 tháng", "3-6 tháng"...

    # Bước 4: Mục tiêu ưu tiên (Mới)
    primary_goal = Column(String(255), nullable=True)  # "Cần việc làm ngay" vs "Lộ trình thăng tiến long-term"

    # Các cột cũ (vẫn giữ để tương thích)
    major_combinations = Column(String(255), nullable=True)
    academic_performance = Column(String(100), nullable=True)
    custom_subject_notes = Column(Text, nullable=True)
    preferred_environment = Column(String(255), nullable=True)
    introvert_scale = Column(Integer, default=3, nullable=True)
    preferred_locations = Column(String(255), nullable=True)
    tuition_budget = Column(String(255), nullable=True)
    top_priority = Column(String(255), nullable=True)
    
    raw_json = Column(Text, nullable=True)  # Toàn bộ JSON form gốc để nạp prompt
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profiles")
    consultations = relationship("ConsultationSession", back_populates="profile")


class ConsultationSession(Base):
    __tablename__ = "consultation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    profile_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=True)
    title = Column(String(255), default="Tư vấn định hướng ngành học")
    
    # Kết quả phân tích ban đầu (Top Job Roles & Skill Gap)
    job_roles_json = Column(Text, nullable=True)
    top_majors_json = Column(Text, nullable=True)  # Giữ cho backward compatibility
    overview_analysis = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="consultations")
    profile = relationship("StudentProfile", back_populates="consultations")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("consultation_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    mode = Column(String(50), default="multidimensional")  # 1: multidimensional, 2: university_detail, 3: market_trend, 4: roleplay
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship
    session = relationship("ConsultationSession", back_populates="messages")


class MajorInfo(Base):
    __tablename__ = "majors_info"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # CNTT, Kinh tế, Kỹ thuật, Y Dược, Xã hội...
    combinations = Column(String(100))  # "A00, A01, D01"
    benchmark_score = Column(String(50))  # "25.5 - 28.0"
    avg_tuition = Column(String(100))  # "25 - 35 triệu/năm"
    starting_salary = Column(String(100))  # "10 - 18 triệu/tháng"
    description = Column(Text)
    curriculum_highlights = Column(Text)  # "Cấu trúc môn học, Môn khó nhất"
    career_opportunities = Column(Text)  # Vị trí việc làm & xu hướng
    roleplay_scenario = Column(Text, nullable=True)  # Kịch bản thử nghiệm 1 ngày làm nghề
