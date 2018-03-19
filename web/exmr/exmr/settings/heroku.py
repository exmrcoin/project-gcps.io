import dj_database_url

from .base import *

ALLOWED_HOSTS = ['get-crypto-payments.herokuapp.com']

# Heroku postgres settings
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)


# For email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_HOST_USER = 'joblejose1@gmail.com'

EMAIL_HOST_PASSWORD = 'techversant'

EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
