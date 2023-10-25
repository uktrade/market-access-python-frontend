from .test import *  # noqa

DJANGO_ENV = "front_end_tests"

MIDDLEWARE.remove("authentication.middleware.SSOMiddleware")
MIDDLEWARE.remove("django.middleware.security.SecurityMiddleware")

BASE_FRONTEND_TESTING_URL = env.str(
    "BASE_FRONTEND_TESTING_URL", default="http://localhost:9001"
)
if BASE_FRONTEND_TESTING_URL.endswith("/"):
    BASE_FRONTEND_TESTING_URL = BASE_FRONTEND_TESTING_URL[:-1]
