<<<<<<< HEAD
﻿"""
Configuration management using Pydantic Settings
Production-ready configuration with validation
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/freelancing_agency"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # JWT
    SECRET_KEY: str = "change-this-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Adzuna API
    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_APP_KEY: Optional[str] = None

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"

    # Application
    DEBUG: bool = False

    # CORS - comma-separated list of allowed origins
    ALLOWED_ORIGINS: str = "http://localhost:8501,http://localhost:3000"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_allowed_origins(self) -> List[str]:
        """Parse allowed origins from comma-separated string"""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


# Global settings instance
settings = Settings()
=======
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
