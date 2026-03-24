from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.transaction import Transaction, TransactionPublic, TransactionType

router = APIRouter(prefix="/transactions", tags=["입출고 내역"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=list[TransactionPublic])
def list_transactions(
    session: SessionDep,
    product_id: Annotated[int | None, Query(description="특정 상품 필터")] = None,
    transaction_type: Annotated[
        TransactionType | None, Query(description="입고/출고 필터")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=200, description="최대 조회 개수")] = 50,
):
    """입출고 내역을 조회합니다. 최신 순으로 반환됩니다."""
    statement = select(Transaction).order_by(Transaction.created_at.desc()).limit(limit)
    if product_id:
        statement = statement.where(Transaction.product_id == product_id)
    if transaction_type:
        statement = statement.where(Transaction.transaction_type == transaction_type)
    return session.exec(statement).all()
