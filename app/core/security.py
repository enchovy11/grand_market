from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.core.config import get_settings
from app.database import get_session

settings = get_settings()
bearer_scheme = HTTPBearer()


def create_access_token(user_id: int, role: str) -> str:
    """JWT 액세스 토큰 생성"""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_session)],
):
    """
    JWT 토큰을 검증하고 현재 로그인 사용자를 반환합니다.
    인증이 필요한 모든 엔드포인트에서 Depends(get_current_user)로 사용합니다.
    """
    from app.models.user import User  # 순환 import 방지

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 토큰입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user


def require_merchant(current_user=Depends(get_current_user)):
    """상인 권한이 필요한 엔드포인트에서 사용"""
    from app.models.user import UserRole
    if current_user.role != UserRole.merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="상인 계정만 사용할 수 있는 기능입니다.",
        )
    return current_user
