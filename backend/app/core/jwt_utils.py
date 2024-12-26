from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings

# Constants
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
security = HTTPBearer()

class TokenError(HTTPException):
    """Custom exception for token-related errors."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

def create_access_token(
    subject: Any,
    expires_delta: Optional[timedelta] = None,
    scopes: list[str] = None,
    extra_claims: Dict[str, Any] = None
) -> str:
    """
    Create a new JWT access token.
    
    Args:
        subject: The subject of the token (usually user_id)
        expires_delta: Optional custom expiration time
        scopes: Optional list of permission scopes
        extra_claims: Optional additional claims to include in the token
    
    Returns:
        str: Encoded JWT token
    """
    claims = {
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    if scopes:
        claims["scopes"] = scopes
        
    if extra_claims:
        claims.update(extra_claims)
    
    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    claims["exp"] = expire

    try:
        return jwt.encode(claims, settings.SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise TokenError(f"Could not create access token: {str(e)}")

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        dict: The decoded token claims
        
    Raises:
        TokenError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        
        # Validate token type
        if payload.get("type") != "access":
            raise TokenError("Invalid token type")
            
        # Validate subject claim
        if "sub" not in payload:
            raise TokenError("Subject identifier missing")
            
        return payload
        
    except JWTError as e:
        raise TokenError(f"Invalid token: {str(e)}")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Get current user from JWT token.
    
    Args:
        credentials: The HTTP Authorization credentials
        
    Returns:
        dict: The decoded user information
        
    Raises:
        TokenError: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        return decode_access_token(token)
    except Exception as e:
        raise TokenError(str(e))
