from enum import Enum
from functools import cached_property
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class InitializationError(Exception):
    pass

class RunMode(Enum):
    PROD = 'prod'
    DEV = 'dev'

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding='utf-8', extra='ignore')

    run_mode: RunMode = 'dev'
    archive_base_dir: Path = Path(__file__).parents[2]
    internal_notification_api_key: str | None = Field(
        default=None,
        description="X-Internal-Notification-Key для POST /v1/user-notifications; в dev пусто = без заголовка.",
    )

    def is_dev(self) -> bool:
        return self.run_mode == RunMode.DEV

    def is_prod(self) -> bool:
        return self.run_mode == RunMode.PROD

class HTTPServerSettings(BaseSettings):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._run_mode = kwargs.get('run_mode', RunMode.DEV.value)

    model_config = SettingsConfigDict(env_file_encoding='utf-8', extra='ignore')

    host: str = "0.0.0.0"
    port: int = 8000
    api_version: str
    origins: list[str] | None = None


    @cached_property
    def origins(self):
        match self._run_mode:
            case RunMode.PROD:
                return self.origins or ['*']
            case RunMode.DEV:
                return self.origins or ['*']
            case _:
                raise InitializationError(f'Unsupported RUN_MODE: {self.RUN_MODE}')

class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding='utf-8', extra='ignore')

    private_key_path: str
    public_key_path: str
    algorithm: str


class NotificationSettings(BaseSettings):
    """Env prefix NOTIFY_. Судьи (JUDGE_EMAILS) используются для писем только если в событии нет user_ids."""

    model_config = SettingsConfigDict(env_file_encoding='utf-8', extra='ignore', env_prefix="NOTIFY_")

    resend_api_key: str | None = None
    mail_from: str | None = None
    judge_emails: str = ""
    webhook_url: str | None = None
