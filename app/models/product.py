from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ProductCategory(str, Enum):
    """식자재 카테고리 (REQ-06 표준 카테고리 분류)"""
    vegetable = "채소"
    fruit = "과일"
    seafood = "수산물"
    meat = "육류"
    grain = "곡물"
    dairy = "유제품"
    other = "기타"


class Product(SQLModel, table=True):
    """상품 테이블 - 판매하는 물건 목록"""

    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: int = Field(foreign_key="store.id", index=True, description="등록한 점포 ID")
    name: str = Field(index=True, description="상품명 (예: 사과, 배추)")
    category: ProductCategory = Field(
        default=ProductCategory.other, description="식자재 카테고리"
    )
    unit: str = Field(default="개", description="단위 (예: 개, kg, 묶음)")
    price: float = Field(gt=0, description="판매 단가 (원)")
    low_stock_threshold: int = Field(
        default=5, ge=0, description="재고 부족 알림 기준 수량"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_active: bool = Field(default=True, description="판매 중 여부")


# ── 요청/응답 스키마 ──────────────────────────────────────────

class ProductCreate(SQLModel):
    """상품 등록 요청 바디"""

    store_id: int
    name: str
    category: ProductCategory = ProductCategory.other
    unit: str = "개"
    price: float = Field(gt=0)
    low_stock_threshold: int = Field(default=5, ge=0)


class ProductUpdate(SQLModel):
    """상품 수정 요청 바디 (일부 필드만 수정 가능)"""

    name: Optional[str] = None
    category: Optional[ProductCategory] = None
    unit: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    low_stock_threshold: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ProductPublic(SQLModel):
    """상품 응답 스키마"""

    id: int
    store_id: int
    name: str
    category: ProductCategory
    unit: str
    price: float
    low_stock_threshold: int
    created_at: datetime
    is_active: bool
