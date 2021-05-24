from enum import Enum
from typing import List, Union

from pydantic import BaseSettings


class LogLevelEnum(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class EasyNotifyerConfig(BaseSettings):
    token: str
    chat_id: Union[str, int, List[int], List[str]]
    service_name: str

    class Config:
        env_prefix = "telegram_"


class AppSettings(BaseSettings):
    debug: bool = False
    log_level: LogLevelEnum = LogLevelEnum.INFO


class DBSettings(BaseSettings):
    uri: str = "sqlite:///db.sqlite3"


class MainConfig(BaseSettings):
    app: AppSettings = AppSettings()
    db: DBSettings = DBSettings()
    telegram: EasyNotifyerConfig = EasyNotifyerConfig()
