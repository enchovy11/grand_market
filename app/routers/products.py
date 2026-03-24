from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.product import Product, ProductCreate, ProductPublic, ProductUpdate

router = APIRouter(prefix="/products", tags=["상품 관리"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=list[ProductPublic])
def list_products(
    session: SessionDep,
    category: Annotated[str | None, Query(description="카테고리 필터")] = None,
    active_only: Annotated[bool, Query(description="판매 중인 상품만 조회")] = True,
):
    """등록된 상품 목록을 조회합니다."""
    statement = select(Product)
    if active_only:
        statement = statement.where(Product.is_active == True)
    if category:
        statement = statement.where(Product.category == category)
    return session.exec(statement).all()


@router.post("/", response_model=ProductPublic, status_code=201)
def create_product(product: ProductCreate, session: SessionDep):
    """새 상품을 등록합니다."""
    db_product = Product.model_validate(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.get("/{product_id}", response_model=ProductPublic)
def get_product(product_id: int, session: SessionDep):
    """특정 상품 정보를 조회합니다."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return product


@router.patch("/{product_id}", response_model=ProductPublic)
def update_product(product_id: int, product_update: ProductUpdate, session: SessionDep):
    """상품 정보를 수정합니다 (일부 필드만 수정 가능)."""
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    update_data = product_update.model_dump(exclude_unset=True)
    db_product.sqlmodel_update(update_data)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, session: SessionDep):
    """상품을 비활성화합니다 (실제 삭제가 아닌 숨김 처리)."""
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    db_product.is_active = False
    session.add(db_product)
    session.commit()
