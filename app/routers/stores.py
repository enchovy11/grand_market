from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import get_current_user, require_merchant
from app.database import get_session
from app.models.store import Store, StoreCreate, StoreRead, StoreUpdate
from app.models.user import User

router = APIRouter(prefix="/stores", tags=["점포"])


@router.post("", response_model=StoreRead, summary="점포 등록 (상인 전용)")
def create_store(
    store_data: StoreCreate,
    current_user: User = Depends(require_merchant),
    session: Session = Depends(get_session),
):
    """상인이 자신의 점포를 등록합니다. 현재 GPS 위치(위도/경도)를 함께 전송하세요."""
    store = Store(**store_data.model_dump(), owner_id=current_user.id)
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@router.get("", response_model=list[StoreRead], summary="주변 점포 목록 조회")
def list_stores(
    lat: float | None = None,
    lng: float | None = None,
    session: Session = Depends(get_session),
):
    """
    등록된 점포 목록을 반환합니다.
    - **lat**, **lng**: 위도/경도를 전달하면 해당 위치 기준 정렬 (현재는 전체 반환, 추후 거리 필터 추가)
    """
    stores = session.exec(select(Store).where(Store.is_open == True)).all()
    return stores


@router.get("/{store_id}", response_model=StoreRead, summary="점포 상세 조회")
def get_store(store_id: int, session: Session = Depends(get_session)):
    """점포 ID로 상세 정보를 조회합니다."""
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="점포를 찾을 수 없습니다.")
    return store


@router.patch("/{store_id}", response_model=StoreRead, summary="점포 정보 수정 (상인 전용)")
def update_store(
    store_id: int,
    update_data: StoreUpdate,
    current_user: User = Depends(require_merchant),
    session: Session = Depends(get_session),
):
    """상인이 자신의 점포 정보를 수정합니다."""
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="점포를 찾을 수 없습니다.")
    if store.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인 점포만 수정할 수 있습니다.")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(store, key, value)

    session.commit()
    session.refresh(store)
    return store
