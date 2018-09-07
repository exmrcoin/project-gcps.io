from .base import *


ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exmr',
        'USER': 'postgres',
        'PASSWORD': 'nV4DS3p2',
        'HOST': 'localhost',
    }
}

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'exmr.test@gmail.com'
EMAIL_HOST_PASSWORD = 'Adminqwerty123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEBUG = True
