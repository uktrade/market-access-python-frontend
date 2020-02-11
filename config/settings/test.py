from .base import *

DJANGO_ENV = "test"

SECRET_KEY = "nothing secret about this one"

TEST_RUNNER = "config.testrunner.PytestTestRunner"

MOCK_METADATA = True

# Overrides to be able to run individual tests from PyCharm
# TEMPLATES[0]["DIRS"].append("/usr/src/app/templates")
# STATIC_ROOT = "/usr/src/app/static"
