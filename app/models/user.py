from enum import Enum
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class UserRole(str, Enum):
    merchant = "merchant"   # 상인
    consumer = "consumer"   # 소비자


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    kakao_id: str = Field(unique=True, index=True, description="카카오 고유 사용자 ID")
    nickname: str = Field(description="카카오 닉네임")
    profile_image: Optional[str] = Field(default=None, description="프로필 이미지 URL")
    role: UserRole = Field(default=UserRole.consumer, description="상인/소비자 구분")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # 관계
    stores: list["Store"] = Relationship(back_populates="owner")
    posts: list["Post"] = Relationship(back_populates="author")


# 응답용 스키마 (비밀 필드 제외)
class UserRead(SQLModel):
    id: int
    nickname: str
    profile_image: Optional[str]
    role: UserRole
