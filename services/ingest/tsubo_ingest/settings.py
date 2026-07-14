from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url_sync: str = "postgresql://tsubo:tsubo@localhost:5432/tsubo"
    redis_url: str = "redis://localhost:6379/0"
    s3_endpoint: str = "http://localhost:9000"
    s3_bucket: str = "tsubo-raw"


settings = IngestSettings()
