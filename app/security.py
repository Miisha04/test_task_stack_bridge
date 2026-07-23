import hashlib
from jose import jwt
from passlib.context import CryptContext

from app.settings import get_settings

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    settings = get_settings()
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    settings = get_settings()
    return jwt.encode(to_encode, settings.jwt_refresh_secret, algorithm=settings.jwt_algorithm)

def hash_refresh(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()