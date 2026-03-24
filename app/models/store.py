from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class Store(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", description="점포 주인 (상인) ID")
    name: str = Field(description="점포 이름")
    description: Optional[str] = Field(default=None, description="점포 설명")
    latitude: float = Field(description="위도 - 카카오맵 마커 표시용")
    longitude: float = Field(description="경도 - 카카오맵 마커 표시용")
    address: Optional[str] = Field(default=None, description="도로명 주소")
    is_open: bool = Field(default=True, description="영업 중 여부")

    # 관계
    owner: Optional["User"] = Relationship(back_populates="stores")


# 점포 생성 요청 스키마
class StoreCreate(SQLModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None


# 점포 수정 요청 스키마
class StoreUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    is_open: Optional[bool] = None


# 응답 스키마 (목록 조회용)
class StoreRead(SQLModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    latitude: float
    longitude: float
    address: Optional[str]
    is_open: bool
