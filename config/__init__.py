# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

import os

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app  # noqa

from xTool.utils import get_env_or_raise

__all__ = ["celery_app", "RUN_VER", "APP_CODE", "SECRET_KEY", "BK_URL", "BASE_DIR"]

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

APP_CODE = get_env_or_raise("BKPAAS_APP_ID", "xxx")
SECRET_KEY = get_env_or_raise("BKPAAS_APP_SECRET", "xxx")
RUN_VER = get_env_or_raise("BKPAAS_ENGINE_REGION", "open")
BK_URL = os.getenv("BKPAAS_URL")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
