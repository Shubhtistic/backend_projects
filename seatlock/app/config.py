from pydantic_settings import BaseSettings, SettingsConfigDict


class DB_CREDENTIALS(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


database_settings = DB_CREDENTIALS()
