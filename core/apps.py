import redis
from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        if settings.DJANGO_ENV != "test":
            redis_client = redis.Redis.from_url(url=settings.REDIS_URI)
            redis_client.delete("metadata")
