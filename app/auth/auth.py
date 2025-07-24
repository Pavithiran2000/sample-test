import jwt
import os
from fastapi import HTTPException, Request
from typing import Optional
import base64
from dotenv import load_dotenv


load_dotenv()

def get_public_key(key_type: str) -> str:
    env_var = f"{key_type.upper()}_TOKEN_PUBLIC_KEY"
    encoded_key = os.getenv(env_var)
    if not encoded_key:
        raise ValueError(f"Environment variable {env_var} is not set")
    try:
        decoded_key = base64.b64decode(encoded_key).decode('utf-8')
        return decoded_key
    except Exception as e:
        raise ValueError(f"Failed to decode {env_var}: {str(e)}")

def verify_token(token: str, token_type: str = 'access') -> dict:
    try:
        public_key = get_public_key(token_type)
        
        payload = jwt.decode(token, public_key, algorithms=["RS256"], options={"verify_signature": False})
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail=f"{token_type.title()} token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid {token_type} token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

def get_token_from_cookie(request: Request, token_name: str) -> Optional[str]:
    return request.cookies.get(token_name)

def get_token_from_header(request: Request) -> Optional[str]:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

async def authenticate_user(request: Request) -> dict:
    try:
        access_token = get_token_from_cookie(request, "access_token") or get_token_from_header(request)
        if not access_token:
            raise HTTPException(status_code=401, detail="Access token required")
        user_payload = verify_token(access_token, 'access')
        return user_payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

def get_current_user(request: Request) -> dict:
    return getattr(request.state, 'user', None)
