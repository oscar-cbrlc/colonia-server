from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(
        alias="DATABASE_URL",
        #TODO(local db): connect local db
        default="postgresql://postgres:@localhost/colonia_local_db"
    )
    api_key: str = Field(alias="API_KEY")
    environment: str = Field(alias="ENVIRONMENT", default="development")

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()