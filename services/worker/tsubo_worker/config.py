from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    temporal_address: str = "localhost:7233"
    temporal_namespace: str = "default"
    task_queue: str = "tsubo-worker"
    api_base_url: str = "http://localhost:8000"


settings = WorkerSettings()
