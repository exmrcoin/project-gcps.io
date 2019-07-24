import json
import ast
import requests
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
from apps.apiapp.coingecko import CoinGeckoAPI
from apps.apiapp.coincap import CoincapAPI
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.template.loader import render_to_string

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

logger = get_task_logger(__name__)




coingecko = CoinGeckoAPI()
coincap = CoincapAPI()

@periodic_task(run_every=(crontab(minute='*/1')), name="check_market_rate", ignore_result=True)
def check_market_rate():
   
    # coin_rate_list = coingecko.get_coins_markets('usd')
    # rates = {(rate['symbol']).upper():rate['current_price'] for rate in coin_rate_list}
    # cache.set('rates', rates, timeout=7200)
    cache.set('last_check',  datetime.now(), timeout=7200)
    coin_rate_list = coincap.get_coins_markets('usd')
    rates = {(rate['symbol']).upper():rate['priceUsd'] for rate in coin_rate_list['data']}
    cache.set('rates', rates, timeout=7200)
    


    # try:
    #     rates = cache.get('rates')
    #     rates = ast.literal_eval(rates)
    # except:
    #     data = json.loads(requests.get("http://coincap.io/front").text)
    #     rates = {rate['short']:rate['price'] for rate in data}
    # print(rates)

@periodic_task(run_every=(crontab(minute='*/10')), name="send_feedback_email_task", ignore_result=True)
def send_feedback_email_task():
    logger.info("check_timedout")
    rates = cache.get('rates')
    # send_mail('check_timedout', 'Balance = '+str(balance)+'address = '+multi_payment.address+'coin = '+multi_payment.code+'rates'+str(rates)+'    '+'market', settings.EMAIL_HOST_USER, ['ebrahimasifismail@gmail.com'], fail_silently=False)
    pending = MerchantPaymentWallet.objects.filter(is_active=True)
    if pending:
        for multi_payment in pending:

            balance = utils.get_balance(multi_payment.merchant, multi_payment.code, multi_payment.address)
            if balance > 0:
                multi_payment.is_active = False
                multi_payment.amount = balance
                curr_rate = rates[multi_payment.code]
                multi_payment.market_rate = balance * curr_rate
                multi_payment.save()
            else:
                pass
            timeleft = timezone.now() - multi_payment.initiated_at 
            if not timeleft < timedelta(hours=1):
                multi_payment.timed_out = True
                multi_payment.save()
            # send_mail('check_timedout', 'Balance = '+str(balance)+'address = '+multi_payment.address+'coin = '+multi_payment.code+'rates'+str(rates)+'    '+'market', settings.EMAIL_HOST_USER, ['ebrahimasifismail@gmail.com'], fail_silently=False)


@periodic_task(run_every=(crontab(minute='*/10')), name="check_multipayment", ignore_result=True)
def check_multipayment():
    # logger.info("multi_payment")
    context = []

    list = SimpleButtonInvoice.objects.filter(payment_status='PENDING')
    
    for invoice in list:
        context.append(invoice.unique_id)
    # logger.info(context)
    # logger.info("\n")
    for item in context:
        queryset = MerchantPaymentWallet.objects.filter(unique_id=item)
        invoice = SimpleButtonInvoice.objects.get(unique_id=item)
        # send_mail('subject' + str(queryset) + '   '+ str(invoice) +str(list), '', settings.EMAIL_HOST_USER, ['ebrahimasifismail@gmail.com'], fail_silently=False)
        merchant_email = Profile.objects.get(merchant_id=invoice.merchant_id).public_email
        details = {
            'merchant_details': queryset,
            'customer_detail': invoice
        }
        rendered = render_to_string('merchant_tools/multipayment_received_mail.html', details)
        if queryset:
            total = 0
            for wallet in queryset:
                total = float(total) + float(wallet.market_rate)     
            if invoice.item_amount <= total:
                invoice.payment_status = 'SUCCESS'
                invoice.save()
                send_mail('MultiPayment Recieved. Invoice Id: ' + str(invoice.unique_id) , rendered, settings.EMAIL_HOST_USER, [merchant_email], fail_silently=False)         

    



    