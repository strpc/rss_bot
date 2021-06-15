from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseSettings


class LogLevelEnum(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class CeleryConfig(BaseSettings):
    broker: str
    hour_beat_interval: str
    minute_beat_interval: str

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


class PocketConfig(BaseSettings):
    consumer_key: str
    redirect_url: str

    class Config:
        env_prefix = "pocket_"


class LimitConfig(BaseSettings):
    load_feed: int
    title: int
    text: int
    count_feed: int

    class Config:
        env_prefix = "limit_"


class AppSettings(BaseSettings):
    debug: bool = False
    log_level: LogLevelEnum = LogLevelEnum.INFO


class DBSettings(BaseSettings):
    url: str
    paramstyle: str = "?"  # SELECT * FROM users WHERE users.id = ?

    class Config:
        env_prefix = "database_"


class MainConfig(BaseSettings):
    app: AppSettings = AppSettings()
    celery: CeleryConfig = CeleryConfig()
    db: DBSettings = DBSettings()
    easy_notifyer: Optional[EasyNotifyerConfig] = EasyNotifyerConfig()
    limits: LimitConfig = LimitConfig()
    telegram: TelegramConfig = TelegramConfig()
    pocket: PocketConfig = PocketConfig()


def get_config() -> MainConfig:
    return MainConfig()
