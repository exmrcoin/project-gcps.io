import os
name = os.environ.get('ENV_NAME')

if name == 'aws':
    from .heroku import *
elif name == 'production':
    from .production import *
elif name == 'local':
    from .local import *
else:
    from .local import *
