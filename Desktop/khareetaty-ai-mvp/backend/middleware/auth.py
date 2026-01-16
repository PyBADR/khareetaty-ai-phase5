"""
Authentication Middleware for Khareetaty AI API
Validates Bearer token from Authorization header
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# Initialize bearer token security
security = HTTPBearer()

# Get the expected auth token from environment
EXPECTED_TOKEN = os.getenv("AUTH_TOKEN", "khareetaty-secure")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the Bearer token in Authorization header
    
    Args:
        credentials: HTTP authorization credentials from FastAPI security
        
    Returns:
        dict: User information if authenticated
        
    Raises:
        HTTPException: 401 if token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Use Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if credentials.credentials != EXPECTED_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Return basic user info for authenticated requests
    return {
        "authenticated": True,
        "token": credentials.credentials,
        "user": "api_client"
    }

async def require_auth(request: Request):
    """
    Middleware function to require authentication for all requests
    Can be applied to specific routes or globally
    
    Args:
        request: FastAPI Request object
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    # Skip authentication for docs and health endpoints
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
        return
    
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Parse Bearer token
    try:
        scheme, token = auth_header.split()
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Use Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if token != EXPECTED_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
