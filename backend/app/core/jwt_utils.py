from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from decouple import config

JWT_SECRET = config('JWT_SECRET_KEY')
JWT_ALGORITHM = 'HS256'
security = HTTPBearer()

def generate_token(user_id: int, email: str) -> dict:
    """Generate JWT tokens for a user."""
    
    # Access token payload
    access_payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=1),  # 1 day expiration
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    # Refresh token payload
    refresh_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30),  # 30 days expiration
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    # Generate tokens
    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }

def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload['type'] != 'access':
            raise HTTPException(status_code=401, detail='Invalid token type')
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

def refresh_access_token(refresh_token: str) -> dict:
    """Generate new access token using refresh token."""
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload['type'] != 'refresh':
            raise HTTPException(status_code=401, detail='Invalid token type')
        
        # Generate new access token
        user_id = payload['user_id']
        new_access_payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        new_access_token = jwt.encode(new_access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        return {
            'access_token': new_access_token,
            'token_type': 'bearer'
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Refresh token has expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid refresh token')

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)
    return payload
