import redis
from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        # deleting the metadata cache on startup, making sure we start from a blank slate when we deploy.
        # we don't want to do this in the test environment, as we don't have access to the redis instance
        if settings.DJANGO_ENV != "test":
            redis_client = redis.Redis.from_url(url=settings.REDIS_URI)
            redis_client.delete("metadata")
