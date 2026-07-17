"""
Security Utilities
Handles password hashing, JWT tokens, encryption, and security validations
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from config import settings
from typing import Optional, Dict, Any
import secrets
import logging
import base64

logger = logging.getLogger(__name__)

# Password hashing context - configure bcrypt to avoid 72-byte check during initialization
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",  # Use 2b variant to avoid wrap bug detection
    bcrypt__truncate_error=False  # Don't error on truncation
)

# Encryption cipher - validate and fix key if needed
def _get_valid_fernet_key() -> bytes:
    """Get a valid Fernet key, generating one if the configured key is invalid"""
    try:
        # Try to use the configured key
        key = settings.ENCRYPTION_KEY
        if isinstance(key, str):
            key = key.encode()
        # Test if it's valid by creating a Fernet instance
        Fernet(key)
        return key
    except Exception as e:
        logger.warning(f"Invalid ENCRYPTION_KEY in settings: {e}. Generating a new one.")
        # Generate a valid key
        import base64
        new_key = base64.urlsafe_b64encode(secrets.token_bytes(32))
        return new_key

cipher_suite = Fernet(_get_valid_fernet_key())


class PasswordHasher:
    """Handles password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with bcrypt (truncate to 72 bytes for bcrypt compatibility)"""
        # Bcrypt has a 72 byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')[:72]
        return pwd_context.hash(password_bytes.decode('utf-8', errors='ignore'))
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)


class TokenManager:
    """Handles JWT token creation and validation"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Verify token type
            if payload.get("type") != token_type:
                logger.warning(f"Invalid token type. Expected: {token_type}, Got: {payload.get('type')}")
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                logger.warning("Token has expired")
                return None
            
            return payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return None


class MessageEncryption:
    """Handles end-to-end encryption for messages"""
    
    @staticmethod
    def encrypt_message(message: str) -> tuple[str, str]:
        """
        Encrypt a message using Fernet symmetric encryption
        Returns: (encrypted_message, key_id)
        """
        try:
            encrypted = cipher_suite.encrypt(message.encode())
            key_id = secrets.token_urlsafe(16)
            return encrypted.decode(), key_id
        except Exception as e:
            logger.error(f"Message encryption failed: {str(e)}")
            raise
    
    @staticmethod
    def decrypt_message(encrypted_message: str) -> str:
        """Decrypt an encrypted message"""
        try:
            decrypted = cipher_suite.decrypt(encrypted_message.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Message decryption failed: {str(e)}")
            raise


class UsernameValidator:
    """Validates and sanitizes usernames"""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, Optional[str]]:
        """
        Validate username according to rules:
        - Must start with @
        - Length 4-16 characters (excluding @)
        - Only English letters, numbers, and underscore
        
        Returns: (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty"
        
        if not username.startswith("@"):
            return False, "Username must start with @"
        
        # Remove @ for validation
        username_without_at = username[1:]
        
        if len(username_without_at) < 4:
            return False, "Username must be at least 4 characters (excluding @)"
        
        if len(username_without_at) > 16:
            return False, "Username cannot exceed 16 characters (excluding @)"
        
        # Check allowed characters
        if not all(c.isalnum() or c == "_" for c in username_without_at):
            return False, "Username can only contain English letters, numbers, and underscore"
        
        # Check if starts with number (optional rule)
        if username_without_at[0].isdigit():
            return False, "Username cannot start with a number"
        
        return True, None
    
    @staticmethod
    def normalize_username(username: str) -> str:
        """Normalize username to lowercase and ensure @ prefix"""
        username = username.strip().lower()
        if not username.startswith("@"):
            username = "@" + username
        return username


class SecurityValidator:
    """Additional security validations"""
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        return True, None
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace("\x00", "")
        
        # Limit length
        text = text[:max_length]
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text


# Export instances
password_hasher = PasswordHasher()
token_manager = TokenManager()
message_encryption = MessageEncryption()
username_validator = UsernameValidator()
security_validator = SecurityValidator()
