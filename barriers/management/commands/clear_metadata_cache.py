from django.conf import settings
from django.core.management.base import BaseCommand

import redis


class Command(BaseCommand):
    help = "Clears the metadata cache"

    def handle(self, *args, **options):
        redis_client = redis.Redis.from_url(url=settings.REDIS_URI)
        redis_client.delete("metadata")
        self.stdout.write(self.style.SUCCESS("Metadata cache cleared"))
