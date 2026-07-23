from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "install_biz",
    broker=str(settings.redis_url),
    backend=str(settings.redis_url),
    include=[
        "app.tasks.download_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)