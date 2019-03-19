import json
import ast
import requests
from celery import Celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger, logger
from django.core.mail import send_mail
from django.conf import settings
from apps.merchant_tools.models import MerchantPaymentWallet, SimpleButtonInvoice
from apps.accounts.models import Profile
from django.utils import timezone
from datetime import timedelta, datetime
from apps.coins import utils
from apps.coins.models import Wallet, WalletAddress
from apps.apiapp.coingecko import CoinGeckoAPI
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.template.loader import render_to_string

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

logger = get_task_logger(__name__)
coingecko = CoinGeckoAPI()


# app = Celery()
@periodic_task(run_every=(crontab(minute='*/1')), name="check_wallet_balance", ignore_result=True)
# @app.task
def check_wallet_balance():
    wallet_list = Wallet.objects.all()
    for wallet in wallet_list:
        for addr in wallet.addresses.all():
            temp_bal = utils.get_balance(wallet.user, wallet.name.code, addr.address)
            cache.set(addr.address,temp_bal)
            temp_obj = WalletAddress.objects.filter(address=addr.address)
            temp_obj.last_check = datetime.now()
            temp_obj.current_balance = temp_bal
            temp_obj.update()

    


# app.conf.beat_schedule = {
#     'add-every-15-minutes': {
#         'task': 'tasks.add',
#         'schedule': 10.0,
#         'args': ()
#     },
# }
# app.conf.timezone = 'UTC'


    