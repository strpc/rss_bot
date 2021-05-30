from enum import Enum
from typing import List, Union

from pydantic import BaseSettings


class LogLevelEnum(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class TelegramConfig(BaseSettings):
    token: str

    class Config:
        env_prefix = "telegram_"


class EasyNotifyerConfig(TelegramConfig):
    chat_id: Union[str, int, List[int], List[str]]
    service_name: str

    class Config:
        env_prefix = "easy_notifyer_"


class AppSettings(BaseSettings):
    debug: bool = False
    log_level: LogLevelEnum = LogLevelEnum.INFO


class DBSettings(BaseSettings):
    path: str = "db.sqlite3"
    paramstyle: str = "?"  # SELECT * FROM users WHERE users.id = ?

    class Config:
        env_prefix = "database_"


class MainConfig(BaseSettings):
    app: AppSettings = AppSettings()
    db: DBSettings = DBSettings()
    easy_notifyer: EasyNotifyerConfig = EasyNotifyerConfig()
    telegram: TelegramConfig = TelegramConfig()


def get_config() -> MainConfig:
    return MainConfig()
