from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exmr',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'e12.ehosts.com'
EMAIL_HOST_USER = 'noreply@getcryptopayments.net'
EMAIL_HOST_PASSWORD = 'Gcp1234!!'
EMAIL_PORT = 587
DEBUG = True