from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "PUT_YOUR_API_KEY_HERE")
    
    # Authentication Keys
    ACCESS_TOKEN_PUBLIC_KEY: str = os.getenv("ACCESS_TOKEN_PUBLIC_KEY")
    REFRESH_TOKEN_PUBLIC_KEY: str = os.getenv("REFRESH_TOKEN_PUBLIC_KEY")
    
    # Server Settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "5000"))
    
    # CORS Settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:5174"
    ]

    GEMINI_API_BASE_URL: str = os.getenv("GEMINI_API_BASE_URL")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL")

    @property
    def gemini_api_url(self) -> str:
        """Construct the complete Gemini API URL"""
        return f"{self.GEMINI_API_BASE_URL}/models/{self.GEMINI_MODEL}:generateContent"

settings = Settings()
