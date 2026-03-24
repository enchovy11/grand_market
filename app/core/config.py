from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 데이터베이스
    database_url: str = "sqlite:///./market_inventory.db"

    # JWT
    secret_key: str = "change-this-to-a-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7일

    # 카카오 API
    kakao_client_id: str = ""

    # KAMIS API
    kamis_api_key: str = ""
    kamis_api_id: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
