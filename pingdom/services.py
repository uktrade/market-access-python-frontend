from django.db import DatabaseError

from healthcheck.models import HealthCheck


class CheckDatabase:
    name = "database"

    def check(self):
        try:
            HealthCheck.objects.exists()
            return True, ""
        except DatabaseError as e:
            return False, e


services_to_check = (CheckDatabase,)
