from django.shortcuts import render
from .poloneix import *
from .binance import *
from apps.coins.models import Coin

# Create your views here.


def createaddr(wallet_name, currency):
    if currency.coin_hosting_type.lower() == 'poloniex':
        return newAddress(currency)
    elif currency.coin_hosting_type.lower()  == 'binance':
        print("inside binance")
        addr = getnewaddress(currency.code)
        return addr
    else:
        return None
