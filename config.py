from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(
        alias="DATABASE_URL",
        #TODO(local db): connect local db
        default="postgresql://postgres:@localhost/colonia_local_db"
    )
    api_key: str = Field(alias="API_KEY")
    jwt_secret: str | None = Field(alias="JWT_SECRET", default=None)
    jwt_expires_minutes: int = Field(alias="JWT_EXPIRES_MINUTES", default=1440)
    environment: str = Field(alias="ENVIRONMENT", default="development")

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()
