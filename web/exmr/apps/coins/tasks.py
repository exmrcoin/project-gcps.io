import json
import ast
import requests
import time
import datetime as utcdatetime
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
from apps.coins import utilscelery as utils
from apps.coins.models import Wallet, WalletAddress, EthereumToken, EthereumTokenWallet
from apps.apiapp.coingecko import CoinGeckoAPI
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.template.loader import render_to_string

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

logger = get_task_logger(__name__)
coingecko = CoinGeckoAPI()

@periodic_task(run_every=(crontab(minute='*/60')), name="check_token_balance", ignore_result=True)    
def check_token_balance():        
    wallet_list = Wallet.objects.exclude(token_name__isnull=True).values_list('token_name','addresses')
    address_list = []
    for tk,t_pk in wallet_list:
        try:
            addr = WalletAddress.objects.get(pk=t_pk).address
            token_code = EthereumToken.objects.get(pk=tk).contract_symbol
            address_list.append((token_code,addr))
        except:
            pass
    
    wallet_list_2 = EthereumTokenWallet.objects.all().values_list('name','addresses')
    for tk,t_pk in wallet_list_2:
        try:
            addr = WalletAddress.objects.get(pk=t_pk).address
            token_code = EthereumToken.objects.get(pk=tk).contract_symbol
            address_list.append((token_code,addr))
        except:
            pass
    address_list = list(set(address_list))

    for x,y in address_list:
        temp_bal = utils.get_balance(None, x, y)
        temp_timestamp = int(time.time())
        temp_var = {}
        temp_var['bal'] = temp_bal
        temp_var['last_checked'] = temp_timestamp
        temp_var['code'] = x
        cache.set(y,temp_var, timeout=7200)

    


@periodic_task(run_every=(crontab(minute='*/60')), name="check_wallet_balance", ignore_result=True)
def check_wallet_balance():
    wallet_list = Wallet.objects.exclude(name__isnull=True)
    for wallet in wallet_list:
        for addr in wallet.addresses.all():
            try:
                temp_bal = utils.get_balance(wallet.user, wallet.name.code, addr.address)
            except:
                try:
                    temp_bal = utils.get_balance(wallet.user, wallet.token_name.contract_symbol, addr.address)
                except:
                    temp_bal = 0
            temp_timestamp = int(time.time())
            temp_var = {}
            temp_var['bal'] = temp_bal
            temp_var['last_checked'] = temp_timestamp
            cache.set(addr.address,temp_var, timeout=7200)
    


