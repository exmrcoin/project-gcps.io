import itertools
from apps.coins.models import Coin, NewCoin, EthereumToken
from itertools import chain
from django.contrib.sites.models import Site


def get_all_coin_code():
    coin_list = []
    main_coins = list(Coin.objects.all().values_list('code', flat=True))
    new_coins = list(NewCoin.objects.all().values_list('code', flat=True))
    eth_tokens = list(EthereumToken.objects.all(
    ).values_list('contract_symbol', flat=True))
    coin_list = main_coins+new_coins+eth_tokens
    return list(set(coin_list))


def get_all_active_coin_code():
    coin_list = []
    main_coins = list(Coin.objects.filter(
        active=True).values_list('code', flat=True))
    new_coins = list(NewCoin.objects.filter(
        approved=True).values_list('code', flat=True))
    eth_tokens = list(EthereumToken.objects.filter(
        display=True).values_list('contract_symbol', flat=True))
    coin_list = main_coins+new_coins+eth_tokens
    return list(set(coin_list))


def get_supported_coin():
    main_coins = Coin.objects.filter(active=True)
    eth_tokens = EthereumToken.objects.filter(display=True)
    temp_coin = {}
    current_site = Site.objects.get_current()
    for coins in main_coins:
        temp_coin[coins.code] = {'coin_name': coins.coin_name,
                                 'coin_code': coins.code, 'image': '//'+current_site.domain+coins.image.url}
    for coins in eth_tokens:
        temp_coin[coins.contract_symbol] = {
            'coin_name': coins.coin_name, 'coin_code': coins.contract_symbol, 'image':'//'+current_site.domain+coins.image.url}    
    return temp_coin
