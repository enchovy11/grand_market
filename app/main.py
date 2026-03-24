from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import inventory, products, transactions
from app.routers import auth, stores


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 이벤트 핸들러"""
    create_db_and_tables()  # 앱 시작 시 DB 테이블 자동 생성
    yield


app = FastAPI(
    title="그랜마켓 API",
    description="""
## 전통시장 재고관리 + 소비자 정보 공유 앱 **그랜마켓** 백엔드

### 주요 기능
- 🔑 **인증**: 카카오 소셜 로그인, JWT 기반 인증
- 🏪 **점포 관리**: 점포 등록·수정·조회 (카카오맵 마커 연동)
- 📦 **재고 관리**: 상품 등록·수정, 실시간 재고 업데이트
- 🔍 **통합 검색**: 키워드 기반 주변 점포 및 상품 검색
- 📋 **커뮤니티**: 시장 정보 공유 게시판
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS 설정 ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 개발용: 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 라우터 등록 ───────────────────────────────────────────────
# 기존 라우터
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(transactions.router)

# Phase 1 - 신규 라우터
app.include_router(auth.router)
app.include_router(stores.router)


@app.get("/", tags=["기본"])
def root():
    """서버 상태 확인용 엔드포인트"""
    return {
        "status": "ok",
        "message": "그랜마켓 서버가 실행 중입니다 🏪",
        "docs": "/docs",
    }
