from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "BIXOO Transportation API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/bixoo_transportation"
    SECRET_KEY: str = "change-this-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: list[str] = []
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def allowed_cors_origins(self) -> list[str]:
        origins = [self.FRONTEND_URL, *self.CORS_ORIGINS]
        if self.APP_ENV.lower() in {"development", "local"}:
            origins.extend([
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:4173",
                "http://127.0.0.1:4173",
            ])
        return list(dict.fromkeys(origin.strip().rstrip("/") for origin in origins if origin.strip()))

settings = Settings()
