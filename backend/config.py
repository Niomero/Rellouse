"""
Application Configuration
Manages all environment variables and application settings
"""
from pydantic_settings import BaseSettings
from typing import List
from cryptography.fernet import Fernet
import secrets
import base64


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    # S3 Storage (Optional)
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET_NAME: str | None = None
    S3_REGION: str = "us-east-1"
    
    # Application
    APP_NAME: str = "Rellouse Messenger"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "https://rellouse.org,http://localhost:3000"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS_PER_USER: int = 5
    
    # Owner Account
    OWNER_USERNAME: str = "Rellouse"
    OWNER_PASSWORD: str = "none"
    OWNER_ADDITIONAL_USERNAMES: str = "admin,user,test,none"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def owner_additional_usernames_list(self) -> List[str]:
        """Parse OWNER_ADDITIONAL_USERNAMES into a list"""
        return [username.strip() for username in self.OWNER_ADDITIONAL_USERNAMES.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
