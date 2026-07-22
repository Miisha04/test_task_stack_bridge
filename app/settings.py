from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, field_validator

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")
    db_name: str = Field(validation_alias="DB_NAME")
    db_host: str = Field(validation_alias="DB_HOST")
    db_port: int = Field(validation_alias="DB_PORT")

    jwt_secret_key: SecretStr = Field(validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_issuer: str = Field(validation_alias="JWT_ISSUER")
    jwt_audience_user: str = Field(validation_alias="JWT_AUDIENCE_USER")
    jwt_access_token_expire_minutes: int = Field(
        default=15,
        validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    jwt_refresh_secret_key: SecretStr = Field(validation_alias="JWT_REFRESH_SECRET_KEY")
    jwt_refresh_token_expire_days: int = Field(validation_alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    jwt_audience_refresh: str = Field(validation_alias="JWT_AUDIENCE_REFRESH")

    @property
    def jwt_secret(self) -> str:
        secret = self.jwt_secret_key.get_secret_value()
        if len(secret) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 chars")
        return secret


    @property
    def jwt_refresh_secret(self) -> str:
        secret = self.jwt_refresh_secret_key.get_secret_value()
        if len(secret) < 32:
            raise ValueError("JWT_REFRESH_SECRET_KEY must be at least 32 chars")
        return secret


@lru_cache
def get_setting() -> Settings:
    return Settings()