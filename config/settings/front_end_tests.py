from .test import *  # noqa

DJANGO_ENV = "front_end_tests"

MIDDLEWARE.remove("authentication.middleware.SSOMiddleware")
MIDDLEWARE.remove("django.middleware.security.SecurityMiddleware")

BASE_TESTING_URL = env.str("BASE_TESTING_URL", default="http://localhost:9001")
