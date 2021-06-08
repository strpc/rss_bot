from enum import Enum
from typing import List, Union

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
    limit_load_feed: int


class DBSettings(BaseSettings):
    url: str = "db.sqlite3"
    paramstyle: str = "?"  # SELECT * FROM users WHERE users.id = ?

    class Config:
        env_prefix = "database_"


class PocketConfig(BaseSettings):
    consumer_key: str

    class Config:
        env_prefix = "pocket_"


class MainConfig(BaseSettings):
    app: AppConfig = AppConfig()
    db: DBSettings = DBSettings()
    celery: CeleryConfig = CeleryConfig()
    easy_notifyer: EasyNotifyerConfig = EasyNotifyerConfig()
    telegram: TelegramConfig = TelegramConfig()
    pocket: PocketConfig = PocketConfig()


def get_config() -> MainConfig:
    return MainConfig()
