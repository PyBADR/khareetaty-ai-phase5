"""
Centralized configuration management for Khareetaty AI
Loads environment variables and provides typed configuration
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseSettings:
    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("DB_PORT", 5432))
    NAME: str = os.getenv("DB_NAME", "khareetaty_ai")
    USER: str = os.getenv("DB_USER", "bader")
    PASSWORD: str = os.getenv("DB_PASSWORD", "secret123")
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

class RedisSettings:
    HOST: str = os.getenv("REDIS_HOST", "localhost")
    PORT: int = int(os.getenv("REDIS_PORT", 6379))
    PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    @property
    def url(self) -> str:
        if self.PASSWORD:
            return f"redis://:{self.PASSWORD}@{self.HOST}:{self.PORT}/0"
        return f"redis://{self.HOST}:{self.PORT}/0"

class JWTSettings:
    SECRET: str = os.getenv("JWT_SECRET", "khareetaty-ai-secret-key-change-in-production-2026")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", 8))

class TwilioSettings:
    ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    WHATSAPP_NUMBER: Optional[str] = os.getenv("TWILIO_WHATSAPP_NUMBER")
    SMS_SENDER: Optional[str] = os.getenv("SMS_SENDER")

class EmailSettings:
    HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    PORT: int = int(os.getenv("SMTP_PORT", 587))
    USER: Optional[str] = os.getenv("SMTP_USER")
    PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    FROM: str = os.getenv("SMTP_FROM", "noreply@khareetaty.ai")

class AlertSettings:
    THRESHOLD: int = int(os.getenv("ALERT_THRESHOLD", 10))
    HIGH_PRIORITY_THRESHOLD: int = int(os.getenv("HIGH_PRIORITY_THRESHOLD", 40))
    CRITICAL_THRESHOLD: int = int(os.getenv("CRITICAL_THRESHOLD", 60))
    ADMIN_PHONE: str = os.getenv("ADMIN_PHONE", "+96566338736")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "bader.naser.ai.sa@gmail.com")

class MLSettings:
    DBSCAN_EPS: float = float(os.getenv("DBSCAN_EPS", 0.02))
    DBSCAN_MIN_SAMPLES: int = int(os.getenv("DBSCAN_MIN_SAMPLES", 5))
    FORECAST_DAYS: int = int(os.getenv("FORECAST_DAYS", 7))

class SchedulerSettings:
    DAILY_JOB_HOUR: int = int(os.getenv("DAILY_JOB_HOUR", 2))
    DAILY_JOB_MINUTE: int = int(os.getenv("DAILY_JOB_MINUTE", 0))

class AppSettings:
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", 8000))
    WORKERS: int = int(os.getenv("API_WORKERS", 4))
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Global settings instance
settings = {
    "database": DatabaseSettings(),
    "redis": RedisSettings(),
    "jwt": JWTSettings(),
    "twilio": TwilioSettings(),
    "email": EmailSettings(),
    "alerts": AlertSettings(),
    "ml": MLSettings(),
    "scheduler": SchedulerSettings(),
    "app": AppSettings()
}

# Export individual settings for convenience
DATABASE = settings["database"]
REDIS = settings["redis"]
JWT = settings["jwt"]
TWILIO = settings["twilio"]
EMAIL = settings["email"]
ALERTS = settings["alerts"]
ML = settings["ml"]
SCHEDULER = settings["scheduler"]
APP = settings["app"]

def get_db_connection_params():
    """Get database connection parameters for psycopg2"""
    return {
        "host": DATABASE.HOST,
        "port": DATABASE.PORT,
        "dbname": DATABASE.NAME,
        "user": DATABASE.USER,
        "password": DATABASE.PASSWORD
    }