import re
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import get_db
from ..db.models import User
from ..core.security import create_token, current_user, hash_password, verify_password, DEMO_USER_ID
from ..core.errors import NextoError, ok

router = APIRouter(prefix="/api/auth", tags=["auth"])
MAX_IMAGE_CHARS = 1_500_000  # data URL 약 1MB


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    name: str | None = None
    photo: str | None = None
    cover: str | None = None
    notes: list[dict] | None = None


def _me(u: User) -> dict:
    return {"user_id": str(u.user_id), "email": u.email, "name": u.name, "photo": u.photo, "cover": u.cover,
            "notes": u.notes or [], "is_demo": str(u.user_id) == DEMO_USER_ID}


def _session(u: User) -> dict:
    return {"token": create_token(str(u.user_id), hours=12 if str(u.user_id) == DEMO_USER_ID else 24 * 7), "user_id": str(u.user_id), "user": _me(u)}


# 데모 세션 발급 (로그인 없이 둘러보기)
@router.post("/demo")
async def demo_session(db: AsyncSession = Depends(get_db)):
    return ok(_session(await db.get(User, DEMO_USER_ID)))


@router.post("/signup")
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    email = req.email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email): raise NextoError("INVALID_EMAIL", "이메일 형식을 확인해 주세요.")
    if len(req.password) < 8: raise NextoError("WEAK_PASSWORD", "비밀번호는 8자 이상으로 정해 주세요.")
    if (await db.execute(select(User).where(func.lower(User.email) == email))).scalars().first():
        raise NextoError("EMAIL_TAKEN", "이미 가입된 이메일이에요. 로그인해 주세요.", status=409)
    user = User(email=email, name=(req.name or "").strip() or email.split("@")[0], password_hash=hash_password(req.password), notes=[])
    db.add(user); await db.commit(); await db.refresh(user)
    return ok(_session(user))


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(func.lower(User.email) == req.email.strip().lower()))).scalars().first()
    if not user or not verify_password(req.password, user.password_hash):
        raise NextoError("INVALID_CREDENTIALS", "이메일 또는 비밀번호가 맞지 않아요.", status=401)
    return ok(_session(user))


@router.get("/me")
async def me(user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user: raise NextoError("UNAUTHORIZED", "다시 로그인해 주세요.", status=401)
    return ok(_me(user))


# 이름·아치 사진·커버 사진·퀵노트 저장
@router.patch("/me")
async def update_me(req: ProfileUpdate, user_id: str = Depends(current_user), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user: raise NextoError("UNAUTHORIZED", "다시 로그인해 주세요.", status=401)
    for key in ("photo", "cover"):
        v = getattr(req, key)
        if v is not None:
            if v and (not v.startswith("data:image/") or len(v) > MAX_IMAGE_CHARS): raise NextoError("INVALID_FILE", "이미지는 1MB 이하 JPG/PNG로 올려 주세요.")
            setattr(user, key, v or None)
    if req.name is not None and req.name.strip(): user.name = req.name.strip()[:100]
    if req.notes is not None: user.notes = [{"text": str(n.get("text", ""))[:200], "done": bool(n.get("done"))} for n in req.notes][:50]
    await db.commit()
    return ok(_me(user))
