from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.inventory import Inventory, InventoryAdjust, InventoryPublic, InventoryStatus
from app.models.product import Product
from app.models.transaction import Transaction, TransactionType

router = APIRouter(prefix="/inventory", tags=["재고 관리"])

SessionDep = Annotated[Session, Depends(get_session)]


def _get_or_create_inventory(session: Session, product_id: int, store_id: int) -> Inventory:
    """상품의 재고 레코드를 가져오거나, 없으면 0으로 새로 생성합니다."""
    inv = session.exec(
        select(Inventory).where(Inventory.product_id == product_id)
    ).first()
    if not inv:
        inv = Inventory(product_id=product_id, store_id=store_id, quantity=0)
        session.add(inv)
        session.commit()
        session.refresh(inv)
    return inv


@router.get("/", response_model=list[InventoryPublic])
def list_inventory(session: SessionDep):
    """전체 재고 현황을 조회합니다."""
    inventories = session.exec(select(Inventory)).all()
    result = []
    for inv in inventories:
        product = session.get(Product, inv.product_id)
        threshold = product.low_stock_threshold if product else 5
        result.append(
            InventoryPublic(
                **inv.model_dump(),
                is_low_stock=inv.quantity <= threshold,
            )
        )
    return result


@router.get("/low-stock", response_model=list[InventoryPublic])
def list_low_stock(session: SessionDep):
    """재고가 부족한 상품 목록을 조회합니다 (시니어 알림용)."""
    inventories = session.exec(select(Inventory)).all()
    result = []
    for inv in inventories:
        product = session.get(Product, inv.product_id)
        threshold = product.low_stock_threshold if product else 5
        if inv.quantity <= threshold:
            result.append(
                InventoryPublic(**inv.model_dump(), is_low_stock=True)
            )
    return result


@router.get("/{product_id}", response_model=InventoryPublic)
def get_inventory(product_id: int, session: SessionDep):
    """특정 상품의 현재 재고를 조회합니다."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    inv = _get_or_create_inventory(session, product_id, product.store_id)
    return InventoryPublic(
        **inv.model_dump(),
        is_low_stock=inv.quantity <= product.low_stock_threshold,
    )


@router.post("/{product_id}/adjust", response_model=InventoryPublic)
def adjust_inventory(product_id: int, body: InventoryAdjust, session: SessionDep):
    """
    재고 수량을 조정합니다 (입고: +양수, 출고: -음수).

    - 수량이 **0이 되면 자동으로 '판매종료'** 상태로 변경됩니다 (REQ-05).
    - `status` 필드로 상태를 직접 변경할 수도 있습니다.
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    inv = _get_or_create_inventory(session, product_id, product.store_id)
    new_qty = inv.quantity + body.quantity_change
    if new_qty < 0:
        raise HTTPException(
            status_code=400,
            detail=f"재고가 부족합니다. 현재 재고: {inv.quantity}개",
        )

    # 재고 업데이트
    inv.quantity = new_qty
    inv.updated_at = datetime.now(timezone.utc)

    # ✅ 수량 0 → 자동 품절 처리 (REQ-05)
    if new_qty == 0:
        inv.status = InventoryStatus.sold_out
    elif body.status:
        inv.status = body.status  # 상태 직접 변경
    else:
        inv.status = InventoryStatus.available  # 재고 있으면 판매중으로 복구

    session.add(inv)

    # 입출고 내역 기록
    tx_type = (
        TransactionType.INCOMING
        if body.quantity_change > 0
        else TransactionType.OUTGOING
    )
    transaction = Transaction(
        product_id=product_id,
        transaction_type=tx_type,
        quantity=abs(body.quantity_change),
        note=body.note,
    )
    session.add(transaction)
    session.commit()
    session.refresh(inv)

    return InventoryPublic(
        **inv.model_dump(),
        is_low_stock=inv.quantity <= product.low_stock_threshold,
    )
