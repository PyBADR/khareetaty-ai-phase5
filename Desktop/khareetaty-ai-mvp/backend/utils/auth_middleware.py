"""
Authentication Middleware for Khareetaty AI API
Handles Bearer token authentication for protected endpoints
"""

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# Get the authentication token from environment
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "khareetaty-secure")
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify Bearer token authentication
    
    Args:
        credentials: HTTP Authorization credentials containing the token
        
    Returns:
        dict: User information if authentication successful
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Return user info (simplified for this implementation)
    return {
        "user_id": "system",
        "role": "admin",
        "authenticated": True
    }

def require_auth(optional: bool = False):
    """
    Dependency for requiring authentication
    
    Args:
        optional: If True, authentication is optional
        
    Returns:
        Function that validates authentication
    """
    def auth_dependency(request: Request):
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            if optional:
                return None
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Authorization header required",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        
        # Parse Bearer token
        if not auth_header.startswith("Bearer "):
            if optional:
                return None
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authorization header format",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        
        token = auth_header.split(" ")[1]
        
        if token != AUTH_TOKEN:
            if optional:
                return None
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        
        return {
            "user_id": "system",
            "role": "admin",
            "authenticated": True
        }
    
    return auth_dependency