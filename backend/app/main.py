from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine, auto_migrate_db
from app.routers import auth, profile, chat, history, admin

# Khởi tạo các bảng cơ sở dữ liệu SQLite nếu chưa tồn tại
Base.metadata.create_all(bind=engine)
auto_migrate_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API cho Chatbot AI Định Hướng Chọn Ngành Đại Học (Đồ Án Chuyên Ngành)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS để Frontend (React/Vue/HTML) thoải mái gọi API
app.add_middleware(
    CORSMiddleware,
    # Bearer token nằm ở header, không dùng cookie → credentials không cần thiết;
    # bật credentials với "*" cho phép mọi site gọi API kèm thông tin đăng nhập
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các Router tính năng
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(profile.router, prefix=settings.API_PREFIX)
import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(history.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_ui():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "project": settings.PROJECT_NAME,
        "status": "Online",
        "documentation": "/docs"
    }

