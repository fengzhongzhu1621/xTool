# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

import os
import sys

from xTool.env import get_env_or_raise

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app  # noqa

__all__ = [
    "celery_app",
    "BASE_DIR",
    "APP_CODE",
    "SECRET_KEY",
    "RUN_VER",
    "BK_URL",
]

APP_CODE = get_env_or_raise("BKPAAS_APP_ID", "xxx")
SECRET_KEY = get_env_or_raise("BKPAAS_APP_SECRET", "xxx")
RUN_VER = get_env_or_raise("BKPAAS_ENGINE_REGION", "open")
BK_URL = os.getenv("BKPAAS_URL")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "apps"))
