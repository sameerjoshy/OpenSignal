from celery import Celery

from config import settings

celery_app = Celery("opensignal", broker=settings.redis_url, backend=settings.redis_url)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    task_default_queue="opensignal",
)

import app.tasks.campaign_tasks  # noqa: E402,F401
import app.tasks.signal_tasks  # noqa: E402,F401
