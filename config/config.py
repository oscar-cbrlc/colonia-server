from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(
        alias="DATABASE_URL",
        #TODO(local db): connect local db
        #default=localdb
    )
    api_key: str = Field(alias="API_KEY")
    environment: str = Field(alias="ENVIRONMENT", DEFAULT="development")

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()