import string

from django.contrib.auth.models import User
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage


from celery import shared_task
from apps.coins.models import Coin

@shared_task
def create_random_user_accounts():
    
    email = EmailMessage('Hello', 'World', to=['anandkrishnan.techversant@gmail.com'])
    email.send()



@periodic_task(run_every=(crontab(minute='*/1')), name="test", ignore_result=True)
def test():
    data = ",".join([obj.coin_name for obj in Coin.objects.all()])
    email = EmailMessage('Hello', data, to=['anandkrishnan.techversant@gmail.com'])
    email.send()
    # do something