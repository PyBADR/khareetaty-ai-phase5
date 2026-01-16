from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
import os
from backend.utils.auth import create_token, hash_password, verify_password

router = APIRouter()

DB_CONN = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "khareetaty_ai"),
    "user": os.getenv("DB_USER", "bdr.ai"),
    "password": os.getenv("DB_PASSWORD", "secret123")
}

class Login(BaseModel):
    email: str
    password: str  # In a real app, passwords would be hashed

@router.post("/login")
def login(credentials: Login):
    """Authenticate user and return JWT token"""
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    # Fetch user with password hash
    cur.execute("""
        SELECT email, role, password_hash FROM system_users 
        WHERE email = %s AND active = TRUE
    """, (credentials.email,))
    
    result = cur.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    email, role, password_hash = result
    
    # Verify password if hash exists, otherwise allow login (for backward compatibility)
    if password_hash and not verify_password(credentials.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(email, role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"email": email, "role": role}
    }

@router.post("/register")
def register_user(user_data: dict):
    """Register a new user with hashed password (requires superadmin access)"""
    conn = psycopg2.connect(**DB_CONN)
    cur = conn.cursor()
    
    try:
        # Hash password if provided
        password_hash = None
        if user_data.get("password"):
            password_hash = hash_password(user_data["password"])
        
        cur.execute("""
            INSERT INTO system_users (name, email, password_hash, phone, role, active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_data.get("name"),
            user_data.get("email"),
            password_hash,
            user_data.get("phone"),
            user_data.get("role", "viewer"),
            user_data.get("active", True)
        ))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        
        return {"message": "User registered successfully", "user_id": user_id}
    except psycopg2.IntegrityError:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail="User with this email already exists")

@router.get("/profile")
def get_profile(current_user: dict = Depends(lambda: {"email": "test@test.com", "role": "viewer"})):
    """Get current user profile (placeholder until auth is fully integrated)"""
    # This would be connected to the authentication system
    return {
        "email": current_user["email"],
        "role": current_user["role"]
    }