from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gcps',
        'USER': 'gcps_admin',
        'PASSWORD': 'Exmr!gcps2019',
        'HOST': 'gcps.ch42z6pwp0th.us-east-2.rds.amazonaws.com',
    }
}



# For email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_SSL = True

EMAIL_HOST = 'just150.justhost.com'

EMAIL_HOST_USER = 'noreply@getcryptopayments.net'

EMAIL_HOST_PASSWORD = 'Exmr@2018'

EMAIL_PORT = 465

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'exmr.test@gmail.com'
# EMAIL_HOST_PASSWORD = 'Adminqwerty123'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# DEBUG = True
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ADMINS = (
   ('ME', 'anandkrishnan.techversant@gmail.com'),
   ('ADMIN', 'vipin.mohan@techversantinc.com'),
)
MANAGERS = ADMINS
