from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = Field(..., env="DB_URL")
    test_db_url: str = Field(..., env="TEST_DB_URL")
    telegram_token: str = Field(..., env="TELEGRAM_TOKEN")
    is_test: bool = Field(..., env="IS_TEST")
    log_level: str = Field(..., env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
