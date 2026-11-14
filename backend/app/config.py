import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Career Guidance Chatbot API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # OpenAI GPT
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    # AI local (Ollama) — ưu tiên nếu bật; phù hợp GPU 4GB VRAM
    OLLAMA_ENABLED: bool = os.getenv("OLLAMA_ENABLED", "True").lower() == "true"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3:4b")  # ~3.3GB Q4, vừa 4GB VRAM
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "career_secret_key_dacn_2026")
    if SECRET_KEY == "career_secret_key_dacn_2026":
        print("[WARN] SECRET_KEY dang dung gia tri mac dinh — dat bien moi truong SECRET_KEY truoc khi deploy!")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./career_guidance.db")
    
    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8080"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()
