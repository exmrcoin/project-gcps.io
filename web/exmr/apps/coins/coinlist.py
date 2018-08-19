import itertools
from apps.coins.models import Coin, NewCoin, EthereumToken


def get_all_coin_code():
    coin_list = []
    main_coins = list(Coin.objects.all().values_list('code',flat=True) )
    new_coins = list(NewCoin.objects.all().values_list('code',flat=True) )
    eth_tokens = list(EthereumToken.objects.all().values_list('contract_symbol',flat=True) )
    coin_list = main_coins+new_coins+eth_tokens
    return list(set(coin_list))

def get_all_active_coin_code():
    coin_list = []
    main_coins = list(Coin.objects.filter(active=True).values_list('code',flat=True) )
    new_coins = list(NewCoin.objects.filter(approved=True).values_list('code',flat=True) )
    eth_tokens = list(EthereumToken.objects.filter(display=True).values_list('contract_symbol',flat=True) )
    coin_list = main_coins+new_coins+eth_tokens
    return list(set(coin_list))