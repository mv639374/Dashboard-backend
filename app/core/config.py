import os
from pathlib import Path
from typing import Optional, List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
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
    
    # CORS Settings - Can accept both string (from .env) or list (from code)
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string to list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace from each origin
            origins = [origin.strip() for origin in v.split(',') if origin.strip()]
            return origins
        elif isinstance(v, list):
            # If already a list, return as is
            return v
        return []
    
    # Database Settings (PostgreSQL)
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "aeo_geo_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    # Excel File Names
    EXCEL_FILE_1_NAME: str = "prod_source_scores_normalized_ranked.xlsx"
    EXCEL_FILE_2_NAME: str = "Book1.xlsx"
    
    # Excel File Paths (constructed from names)
    @property
    def EXCEL_FILE_1(self) -> Path:
        return DATA_DIR / self.EXCEL_FILE_1_NAME
    
    @property
    def EXCEL_FILE_2(self) -> Path:
        return DATA_DIR / self.EXCEL_FILE_2_NAME
    
    @property
    def EXCEL_FILE_3(self) -> Optional[Path]:
        return None
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create settings instance
settings = get_settings()

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
