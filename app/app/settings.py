from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    ROOT_DIR: Path = Path(__file__).parent.parent.resolve()

    # DB settings
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "db"
    DB_HOST: str = "localhost"
    PORT_DB: int = 5432

    @computed_field
    def database_uri(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.PORT_DB}/{self.DB_NAME}"
        )


settings = Config()
