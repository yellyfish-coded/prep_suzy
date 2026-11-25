from celery import Celery

from app.core.config import settings

celery = Celery("prep_suzy", broker=settings.redis_url, include=["app.workers.tasks"])
celery.conf.update(
    task_acks_late=True,
    task_time_limit=120,
    worker_prefetch_multiplier=1,
)