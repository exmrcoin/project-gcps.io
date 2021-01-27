from .base import *
import redis


ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '*']


redis_object = redis.StrictRedis(host='localhost',
	port='6379',
	password='',
	db=0, charset="utf-8", decode_responses=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exmr',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
    }
}

SESSION_EXPIRE_SECONDS = 6000
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'exmr.test@gmail.com'
EMAIL_HOST_PASSWORD = 'Adminqwerty123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEBUG = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

PAYPAL_MODE = "sandbox"
PAYPAL_CLIENT_ID = "AblPqPuQrjYiRqrrwfrokV0qBZf2rxt7S76SzcIY3qAHkRga8Jo_yPebqg50y7MUu8NdEMpJGa-LesfL"
PAYPAL_CLIENT_SECRET = "ECWvEr9uhPoJgIIy4-ali1gi29Mjj63tMOVpihQPnlHr-YtaMsDxfY_pAJUqq7CA5UlrUaVykgfxdHCZ"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        'LOCATION': 'localhost:6379',
        "OPTIONS": {
            "DB": 1,
	    "PASSWORD": "hr_redis", 
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    }
}
CACHE_TTL = 72000
