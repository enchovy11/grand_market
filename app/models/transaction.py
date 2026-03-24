from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel


class TransactionType(str, Enum):
    """입출고 유형"""

    INCOMING = "입고"   # 물건이 들어옴
    OUTGOING = "출고"   # 물건이 나감
    ADJUSTMENT = "조정"  # 재고 수동 조정


class Transaction(SQLModel, table=True):
    """입출고 내역 테이블"""

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    transaction_type: TransactionType
    quantity: int = Field(description="변경 수량 (항상 양수, 방향은 type으로 구분)")
    note: str | None = Field(default=None, description="메모")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── 응답 스키마 ──────────────────────────────────────────

class TransactionPublic(SQLModel):
    """입출고 내역 응답 스키마"""

    id: int
    product_id: int
    transaction_type: TransactionType
    quantity: int
    note: str | None
    created_at: datetime
