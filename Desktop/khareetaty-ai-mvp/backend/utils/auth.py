import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
# Passlib is optional for MVP - install with: pip install passlib[bcrypt]
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False
    print("Warning: passlib not installed. Password hashing disabled.")

SECRET = os.getenv("JWT_SECRET", "insecure-default-secret-change-in-production")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_token(email: str, role: str):
    """Create JWT token for user authentication"""
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token: str = Depends(oauth2_scheme)):
    """Decode JWT token for authentication"""
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid or malformed token")

def verify_role(required_role: str):
    """Decorator to verify user role"""
    def role_checker(token_data: dict = Depends(decode_token)):
        if token_data.get("role") != required_role and token_data.get("role") != "superadmin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return token_data
    return role_checker

def require_role(allowed_roles: list):
    """Decorator to require one of multiple roles"""
    def role_checker(token_data: dict = Depends(decode_token)):
        user_role = token_data.get("role")
        if user_role not in allowed_roles and user_role != "superadmin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return token_data
    return role_checker

class Token(BaseModel):
    access_token: str
    token_type: str

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    if not PASSLIB_AVAILABLE:
        # Fallback: return plain password (INSECURE - for development only)
        return password
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    if not PASSLIB_AVAILABLE:
        # Fallback: simple comparison (INSECURE - for development only)
        return plain_password == hashed_password
    return pwd_context.verify(plain_password, hashed_password)

class LoginRequest(BaseModel):
    email: str
    password: str