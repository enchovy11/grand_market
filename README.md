# 🏪 그랜마켓 (GrandMarket)

> 전통시장 활성화를 위한 재고 관리 및 소비자 정보 공유 앱

상인에게는 간편한 재고 관리 환경을, 소비자에게는 전통시장 장보기 정보를 제공하여 전통시장의 접근성을 높이는 것을 목적으로 합니다.

---

## 🛠 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | Python, Kotlin |
| 백엔드 프레임워크 | FastAPI |
| ORM | SQLModel |
| 데이터베이스 | SQLite (개발) → PostgreSQL (배포 예정) |
| 인증 | 카카오 소셜 로그인 + JWT |
| 외부 API | 카카오맵 API, KAMIS 농수산물 시세 API |

---

## 📁 프로젝트 구조

```
app/
├── main.py               # 서버 진입점, 라우터 등록
├── database.py           # DB 연결 설정
├── core/
│   ├── config.py         # 환경변수 관리 (.env)
│   └── security.py       # JWT 생성·검증, 인증 의존성
├── models/
│   ├── user.py           # 사용자 (상인 / 소비자)
│   ├── store.py          # 점포 (위치 포함)
│   ├── product.py        # 상품 (카테고리, 가격)
│   ├── inventory.py      # 재고 (수량, 판매 상태)
│   ├── transaction.py    # 입출고 내역
│   └── post.py           # 커뮤니티 게시글
└── routers/
    ├── auth.py           # 카카오 로그인, JWT 발급
    ├── stores.py         # 점포 CRUD
    ├── products.py       # 상품 CRUD
    ├── inventory.py      # 재고 관리, 자동 품절 처리
    └── transactions.py   # 입출고 내역
```

---

## 🚀 로컬 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/enchovy11/grand_market.git
cd grand_market
```

### 2. 가상환경 생성 및 패키지 설치
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env.example`을 `.env`로 복사 후 값 입력:
```
KAKAO_CLIENT_ID=카카오_REST_API_키
SECRET_KEY=랜덤_시크릿_키
DATABASE_URL=sqlite:///./market_inventory.db
```

### 4. 서버 실행
```bash
uvicorn app.main:app --reload
```

브라우저에서 **http://localhost:8000/docs** 접속 → Swagger UI에서 API 테스트 가능

---

## 📡 주요 API 엔드포인트

| Method | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/auth/kakao` | 카카오 로그인 / 자동 회원가입 | ❌ |
| GET | `/auth/me` | 내 정보 조회 | ✅ |
| GET | `/stores` | 주변 점포 목록 | ❌ |
| POST | `/stores` | 점포 등록 | ✅ 상인 |
| PATCH | `/stores/{id}` | 점포 정보 수정 | ✅ 상인 |
| GET | `/products` | 상품 목록 조회 | ❌ |
| POST | `/products` | 상품 등록 | ✅ |
| POST | `/inventory/{id}/adjust` | 재고 수량 조정 (0이 되면 자동 품절) | ✅ |
