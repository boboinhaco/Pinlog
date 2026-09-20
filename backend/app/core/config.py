from pydantic_settings import BaseSettings, SettingsConfigDict


# .env 기반 설정
class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://nexto:nexto@localhost:5432/nexto"
    llm_api_key: str = ""
    llm_model: str = "gemini-3.6-flash"
    llm_fallback_models: str = "gemini-3.5-flash-lite,gemini-flash-latest"   # 한도·장애 시 순서대로 대체
    web_search_api_key: str = ""
    public_data_api_key: str = ""
    kakao_rest_api_key: str = ""
    storage_dir: str = "./uploads"
    static_dir: str = ""            # 프론트 빌드 결과 폴더 (배포 이미지에서만 설정, 비우면 API만)
    jwt_secret: str = "change-me-please-32-bytes-minimum!!"
    demo_mode: bool = True
    cors_origins: str = "http://localhost:5173"
    job_hard_timeout_sec: int = 120

    # compose용 POSTGRES_* 같은 모르는 env는 무시
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
