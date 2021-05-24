import os
import sys
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.insert(0, str(BASE_DIR.parent))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "hello_world")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", False) in ("True", "true")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", os.getenv("ALLOWED_HOSTS")]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bot",
]

if DEBUG is True:
    INSTALLED_APPS.append("sslserver")


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("DB_PATH", "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

STATIC_DIR = BASE_DIR / "static"

if DEBUG is False:
    STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# RSS_BOT_TOKEN = os.getenv("RSS_BOT_TOKEN")
# RSS_BOT_BROKER = os.getenv("RSS_BOT_BROKER")
# if all([RSS_BOT_TOKEN, RSS_BOT_BROKER]) is False:
#     raise ValueError(f"Config values is not found. {RSS_BOT_TOKEN=}, {RSS_BOT_BROKER=}")
#
# BASE_URL_TELEGRAM_API = os.getenv("BASE_URL_TELEGRAM_API", "https://api.telegram.org/")
# INTERVAL_BEAT_MINUTE = os.getenv("INTERVAL_BEAT_MINUTE", "5")
# INTERVAL_BEAT_HOUR = os.getenv("INTERVAL_BEAT_HOUR", "*")
#
# ATTEMPT_REQUEST = int(os.getenv("ATTEMPT_REQUEST", 5))  # count of retry
# DELAY_REQUEST = int(os.getenv("DELAY_REQUEST", 3))  # in sec
#
# PARSE_MODE_MARKDOWN = "Markdown"
#
# COUNT_TITLE_SYMBOL = int(os.getenv("COUNT_TITLE_SYMBOL", 500))
# COUNT_TEXT_SYMBOL = int(os.getenv("COUNT_TEXT_SYMBOL", 250))
# COUNT_ARTICLE_UPDATE = int(os.getenv("COUNT_ARTICLE_UPDATE", 5))
# COUNT_FEED_FOR_ADD = int(os.getenv("COUNT_FEED_FOR_ADD"))

LOGS_ROOT = BASE_DIR / "log"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "main_formatter": {
            "format": "%(asctime)s |\t%(levelname)s\t| %(module)s: %(funcName)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG" if DEBUG is True else "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "main_formatter",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}