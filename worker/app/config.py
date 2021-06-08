from enum import Enum
from typing import List, Optional, Union

from pydantic import AnyUrl, BaseSettings


class LogLevelEnum(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class CeleryConfig(BaseSettings):
    broker: AnyUrl
    hour_beat_interval: str = "*"
    minute_beat_interval: str = "*"

    class Config:
        env_prefix = "celery_"


class TelegramConfig(BaseSettings):
    token: str

    class Config:
        env_prefix = "telegram_"


class EasyNotifyerConfig(TelegramConfig):
    chat_id: Union[str, int, List[int], List[str]]
    service_name: str

    class Config:
        env_prefix = "easy_notifyer_"


class AppConfig(BaseSettings):
    debug: bool = False
    log_level: LogLevelEnum = LogLevelEnum.INFO

    class Config:
        env_prefix = "app_"


class DBSettings(BaseSettings):
    url: str = "db.sqlite3"
    paramstyle: str = "?"  # SELECT * FROM users WHERE users.id = ?

    class Config:
        env_prefix = "database_"


class PocketConfig(BaseSettings):
    consumer_key: str

    class Config:
        env_prefix = "pocket_"


class LimitConfig(BaseSettings):
    load_feed: int
    title: int
    text: int

    class Config:
        env_prefix = "limit_"


class MainConfig(BaseSettings):
    app: AppConfig = AppConfig()
    db: DBSettings = DBSettings()
    celery: CeleryConfig = CeleryConfig()
    easy_notifyer: Optional[EasyNotifyerConfig] = EasyNotifyerConfig()
    telegram: TelegramConfig = TelegramConfig()
    pocket: PocketConfig = PocketConfig()
    limits: LimitConfig = LimitConfig()


def get_config() -> MainConfig:
    return MainConfig()
