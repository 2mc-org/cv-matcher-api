from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    """Main service settings"""

    # Service info
    SERVICE_NAME: str = "cv-matcher"
    VERSION: str = "1.0.0"
    
    # API settings
    API_PREFIX: str = "/api/v1"
    
    # Debug mode
    DEBUG: bool = True

    # Main service settings
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database APP settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "test"
    POSTGRES_PORT: int = 5432

    # Database Checkpointer settings
    POSTGRES_CHECKPOINTER_SERVER: str = "localhost"
    POSTGRES_CHECKPOINTER_USER: str = "postgres"
    POSTGRES_CHECKPOINTER_PASSWORD: str = "password"
    POSTGRES_CHECKPOINTER_DB: str = "test_checkpointer"
    POSTGRES_CHECKPOINTER_PORT: int = 5432

    # Redis settings
    REDIS_URL: str = "redis://redis:6379"

    # Qdrant vector DB (docker-compose maps host 6343 → container 6333)
    QDRANT_URL: str = "http://localhost:6343"
    QDRANT_CV_COLLECTION: str = "cv_chunks"
    # Path to a private CV snapshot JSON; empty uses the bundled sample profiles
    CV_SNAPSHOT_PATH: str = ""
    CV_EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"
    CV_SPARSE_EMBEDDING_MODEL: str = "prithivida/Splade_PP_en_v1"

    # Grok API key
    GROK_API_KEY: str = ""

    # Anthropic API key
    ANTHROPIC_API_KEY: str = ""

    POSTGRES_CHECKPOINTER_POOL_MIN_SIZE: int = 0
    POSTGRES_CHECKPOINTER_POOL_MAX_SIZE: int = 3

    def get_db_url(self, async_driver: bool) -> str:
        url = URL.create(
            drivername="postgresql+asyncpg" if async_driver else "postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            database=self.POSTGRES_DB,
            port=self.POSTGRES_PORT,
        )

        return url.render_as_string(hide_password=False)

    def get_checkpointer_db_url(self) -> str:
        """Psycopg DSN for LangGraph AsyncPostgresSaver (not asyncpg)."""
        url = URL.create(
            drivername="postgresql",
            username=self.POSTGRES_CHECKPOINTER_USER,
            password=self.POSTGRES_CHECKPOINTER_PASSWORD,
            host=self.POSTGRES_CHECKPOINTER_SERVER,
            database=self.POSTGRES_CHECKPOINTER_DB,
            port=self.POSTGRES_CHECKPOINTER_PORT,
        )

        return url.render_as_string(hide_password=False)

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )


# Create settings instance
environments = Settings()
