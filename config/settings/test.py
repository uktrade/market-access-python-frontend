from .base import *  # noqa

DJANGO_ENV = "test"

SECRET_KEY = "nothing secret about this one"  # pragma: allowlist secret

TEST_RUNNER = "config.testrunner.PytestTestRunner"

WHITENOISE_AUTOREFRESH = True

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


HEADLESS = env.bool("HEADLESS", default=True)

BASE_FRONTEND_TESTING_URL = env.str(
    "BASE_FRONTEND_TESTING_URL", default="http://web:9000"
)
if BASE_FRONTEND_TESTING_URL.endswith("/"):
    BASE_FRONTEND_TESTING_URL = BASE_FRONTEND_TESTING_URL[:-1]
