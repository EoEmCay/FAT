"""
Centralized configuration for the entire system
Loads from .env file and environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional
import pytz
import os

class Settings(BaseSettings):
    """Centralized configuration"""

    # ============ DATABASE ============
    database_url: str
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str

    # ============ OLLAMA (Local AI) ============
    use_ollama: bool = True
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # ============ GROQ API (ưu tiên 1 — miễn phí, nhanh) ============
    groq_api_key: str = ""

    # ============ OPENAI API (ưu tiên 2 — paid) ============
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo"
    openai_model_mini: str = "gpt-4o-mini"

    # ============ FACEBOOK API ============
    facebook_access_token: str
    facebook_page_id: str
    facebook_api_version: str = "v18.0"

    # ============ SCRAPING ============
    github_token: Optional[str] = None
    huggingface_token: Optional[str] = None
    unsplash_access_key: str = "test_key"
    pexels_api_key: str = "test_key"

    # ============ SCHEDULER ============
    scheduler_timezone: str = "Asia/Ho_Chi_Minh"
    # Lần 1 (buổi sáng)
    scraper_time: str = "06:00"
    processor_time: str = "07:00"
    publisher_time: str = "08:00"
    # Lần 2 (buổi chiều)
    scraper_time_2: str = "14:00"
    processor_time_2: str = "15:00"
    publisher_time_2: str = "16:00"

    # ============ LOGGING ============
    log_level: str = "INFO"
    log_file: str = "logs/orchestrator.log"
    sentry_dsn: Optional[str] = None

    # ============ NOTIFICATIONS (DISABLED) ============
    # Telegram and Email notifications removed

    # ============ STREAMLIT ============
    streamlit_server_port: int = 8501
    streamlit_server_address: str = "0.0.0.0"
    streamlit_logger_level: str = "info"

    class Config:
        env_file = ".env"
        case_sensitive = False

# Load settings
settings = Settings()

# Timezone
TZ = pytz.timezone(settings.scheduler_timezone)

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
