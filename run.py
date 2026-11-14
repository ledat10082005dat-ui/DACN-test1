import sys
import os

# Đảm bảo đường dẫn import app từ thư mục backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), "backend"))

import uvicorn
from app.config import settings
from app.main import app

if __name__ == "__main__":
    print(f"🚀 Dang khoi chay {settings.PROJECT_NAME} tai http://localhost:{settings.PORT}")
    print(f"📖 Swagger API Docs co san tai: http://localhost:{settings.PORT}/docs")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=settings.PORT,
        reload=False
    )
