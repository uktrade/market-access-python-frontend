from .base import *

DJANGO_ENV = "dev"

# SASS settings
# Always compress Sass files
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
LIBSASS_OUTPUT_STYLE = "compressed"
