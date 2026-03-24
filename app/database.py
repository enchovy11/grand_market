from sqlmodel import SQLModel, Session, create_engine

# SQLite 데이터베이스 파일 경로 (개발용)
# 나중에 PostgreSQL 등으로 교체 시 이 URL만 변경하면 됩니다
DATABASE_URL = "sqlite:///./market_inventory.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # SQL 쿼리 로그 출력 (개발 시 유용, 배포 시 False로 변경)
    connect_args={"check_same_thread": False},  # SQLite 전용 설정
)


def create_db_and_tables():
    """앱 시작 시 데이터베이스 테이블 생성"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """API 엔드포인트에서 사용할 DB 세션 의존성"""
    with Session(engine) as session:
        yield session
