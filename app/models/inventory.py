from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class InventoryStatus(str, Enum):
    """재고 판매 상태 (REQ-05)"""
    available = "판매중"
    sold_out = "판매종료"


class Inventory(SQLModel, table=True):
    """재고 테이블 - 상품별 현재 재고 수량 및 상태"""

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True, description="상품 ID")
    store_id: int = Field(foreign_key="store.id", index=True, description="점포 ID")
    quantity: int = Field(default=0, ge=0, description="현재 재고 수량")
    status: InventoryStatus = Field(
        default=InventoryStatus.available, description="판매 상태"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ── 요청/응답 스키마 ──────────────────────────────────────────

class InventoryPublic(SQLModel):
    """재고 응답 스키마"""

    id: int
    product_id: int
    store_id: int
    quantity: int
    status: InventoryStatus
    updated_at: datetime
    is_low_stock: bool = False  # 재고 부족 여부 (라우터에서 계산)


class InventoryAdjust(SQLModel):
    """재고 수량 조정 요청 바디"""

    quantity_change: int = Field(
        description="재고 변경량 (입고: 양수, 출고: 음수, 예: +10 또는 -3)"
    )
    note: Optional[str] = Field(default=None, description="메모 (예: 아침 입고분)")
    status: Optional[InventoryStatus] = Field(
        default=None, description="상태 직접 변경 시 사용 (예: 판매종료)"
    )
