from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.security import create_access_token, get_current_user
from app.database import get_session
from app.models.user import User, UserRead, UserRole

router = APIRouter(prefix="/auth", tags=["인증"])
settings = get_settings()

KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


@router.post("/kakao", summary="카카오 로그인 / 자동 회원가입")
async def kakao_login(
    kakao_access_token: str,
    role: UserRole = UserRole.consumer,
    session: Session = Depends(get_session),
):
    """
    안드로이드 앱에서 카카오 SDK로 받은 **access_token**을 전달하면
    서버가 카카오 API로 사용자 정보를 확인한 뒤 JWT를 발급합니다.

    - **kakao_access_token**: 앱에서 카카오 로그인 후 받은 액세스 토큰
    - **role**: 첫 가입 시 역할 선택 (`merchant` = 상인, `consumer` = 소비자)
    """
    # 카카오 API로 사용자 정보 조회
    async with httpx.AsyncClient() as client:
        response = await client.get(
            KAKAO_USER_INFO_URL,
            headers={"Authorization": f"Bearer {kakao_access_token}"},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 카카오 토큰입니다.",
        )

    kakao_data = response.json()
    kakao_id = str(kakao_data["id"])
    kakao_account = kakao_data.get("kakao_account", {})
    profile = kakao_account.get("profile", {})
    nickname = profile.get("nickname", "익명")
    profile_image = profile.get("profile_image_url")

    # DB에서 기존 사용자 조회
    user = session.exec(select(User).where(User.kakao_id == kakao_id)).first()

    if not user:
        # 신규 회원가입
        user = User(
            kakao_id=kakao_id,
            nickname=nickname,
            profile_image=profile_image,
            role=role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    # JWT 발급
    token = create_access_token(user_id=user.id, role=user.role.value)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user),
    }


@router.get("/me", response_model=UserRead, summary="내 정보 조회")
def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인된 사용자의 정보를 반환합니다."""
    return current_user
