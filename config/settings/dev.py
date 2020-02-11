from .base import *  # noqa

DJANGO_ENV = 'dev'

# SASS settings
# Always compress Sass files
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
LIBSASS_OUTPUT_STYLE = 'compressed'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
