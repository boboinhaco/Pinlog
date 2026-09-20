import hashlib, hmac, secrets
from datetime import datetime, timedelta, timezone
from fastapi import Header
from jose import jwt, JWTError
from .config import settings
from .errors import NextoError

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


# 비밀번호 해시: PBKDF2-SHA256 (salt$hash)
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"{salt}${hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 200_000).hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored or "$" not in stored: return False
    salt, digest = stored.split("$", 1)
    return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex(), digest)


# 세션 JWT 발급 (데모 12시간, 로그인 7일)
def create_token(user_id: str, hours: int = 12) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(hours=hours)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


# Authorization 헤더에서 user_id 추출, 없으면 데모 사용자
def current_user(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        return DEMO_USER_ID
    try:
        return jwt.decode(authorization.removeprefix("Bearer "), settings.jwt_secret, algorithms=["HS256"])["sub"]
    except JWTError:
        raise NextoError("UNAUTHORIZED", "세션이 만료됐어요.", status=401)
