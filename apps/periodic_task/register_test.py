import pytest
from celery.schedules import crontab

from apps.periodic_task.register import register_periodic_task

pytestmark = pytest.mark.django_db


@register_periodic_task(run_every=crontab(minute="*/1"))
def test_register_periodic_task():
    pass
