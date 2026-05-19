from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "voice_ai_db"

    EXOTEL_API_KEY: str = ""
    EXOTEL_API_TOKEN: str = ""
    EXOTEL_SUBDOMAIN: str = "api.exotel.com"
    EXOTEL_SID: str = ""
    EXOTEL_CALLER_ID: str = ""
    EXOTEL_APP_ID: str = ""

    GOOGLE_API_KEY: str = ""

    BASE_URL: str = "http://localhost:8000"
    PORT: int = 8000

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173"
    )


settings = Settings()
