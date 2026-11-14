from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# SQLite connection args
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency cung cấp Session Database cho FastAPI route"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def auto_migrate_db():
    """Tự động kiểm tra và thêm các cột mới vào SQLite DB nếu chưa có"""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    with engine.connect() as conn:
        try:
            # Kiểm tra student_profiles
            result = conn.execute(text("PRAGMA table_info(student_profiles)"))
            cols = [r[1] for r in result.fetchall()]
            if cols:
                expected_cols = {
                    "user_group": "VARCHAR(255)",
                    "current_education_major": "VARCHAR(255)",
                    "known_skills": "TEXT",
                    "experience_years": "VARCHAR(100)",
                    "target_career": "VARCHAR(255)",
                    "expected_salary": "VARCHAR(100)",
                    "learning_time": "VARCHAR(100)",
                    "primary_goal": "VARCHAR(255)"
                }
                for c_name, c_type in expected_cols.items():
                    if c_name not in cols:
                        conn.execute(text(f"ALTER TABLE student_profiles ADD COLUMN {c_name} {c_type}"))
                conn.commit()

            # Kiểm tra consultation_sessions
            res_sess = conn.execute(text("PRAGMA table_info(consultation_sessions)"))
            cols_sess = [r[1] for r in res_sess.fetchall()]
            if cols_sess and "job_roles_json" not in cols_sess:
                conn.execute(text("ALTER TABLE consultation_sessions ADD COLUMN job_roles_json TEXT"))
                conn.commit()
        except Exception as e:
            print(f"Auto-migration notice: {e}")
