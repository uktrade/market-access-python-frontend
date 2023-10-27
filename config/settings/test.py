from .base import *  # noqa

DJANGO_ENV = "test"

SECRET_KEY = "nothing secret about this one"  # pragma: allowlist secret

TEST_RUNNER = "config.testrunner.PytestTestRunner"

MOCK_METADATA = True

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

# Playwright Integration test
BASE_FRONTEND_TESTING_URL = env("BASE_FRONTEND_TESTING_URL")
HEADLESS = True
