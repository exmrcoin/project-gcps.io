import os
name = os.environ.get('ENV_NAME')

if name == 'heroku':
    from .heroku import *
elif name == 'production':
    from .production import *
elif name == 'local':
    from .local import *
else:
    from .base import *
