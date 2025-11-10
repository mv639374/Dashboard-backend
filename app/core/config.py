import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "app" / "data"


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API Settings
    API_TITLE: str = "AEO/GEO Analytics API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Answer Engine Optimization & Generative Engine Optimization Analytics Dashboard"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True
    
    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Database Settings (PostgreSQL)
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "aeo_geo_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    # Excel File Paths
    EXCEL_FILE_1: Path = DATA_DIR / "prod_source_scores_normalized_ranked.xlsx"
    EXCEL_FILE_2: Path = DATA_DIR / "Book1.xlsx"
    EXCEL_FILE_3: Optional[Path] = None
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create settings instance
settings = get_settings()

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
