from .base import *  # noqa

DJANGO_ENV = "test"

SECRET_KEY = "nothing secret about this one"

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

# Overrides to be able to run individual tests from PyCharm
# TEMPLATES[0]["DIRS"].append("/usr/src/app/templates")
# STATIC_ROOT = "/usr/src/app/static"
