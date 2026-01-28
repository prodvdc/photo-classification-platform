from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "photo-classification-api"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/photo_platform"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123"
    classifier_url: str = "http://classifier:8001"
    storage_path: str = "/data/photos"
    max_upload_bytes: int = 5 * 1024 * 1024

    class Config:
        env_file = ".env"


settings = Settings()
