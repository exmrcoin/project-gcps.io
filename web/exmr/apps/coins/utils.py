import json
import requests

from bitcoinrpc.authproxy import AuthServiceProxy
from apps.coins.models import Wallet, WalletAddress, Coin


def create_BTC_connection():
    """
    create connetion to bitcoin fullnode
    """
    access = AuthServiceProxy("http://anand:anandkrishnan@18.218.176.0:18332")
    return access


def create_wallet(user, currency):
    """
    create an account name in full node
    """
    coin = Coin.objects.get(code=currency)
    wallet_username = user.username + "_exmr"
    access = globals()['create_'+currency+'_connection']()
    print (access)
    try:
        # addr = access.getnewaddress(wallet_username)
        addr = False
        raise Exception
    except:
        addr = 'unable to generate address , please try later'
    wallet, created = Wallet.objects.get_or_create(user=user, name=coin)
    wallet.addresses.add(WalletAddress.objects.create(address=addr))
    return addr


def get_balance(user, currency):
    """
    Retrive specified user wallet balance.
    """
    wallet_username = user.username + "_exmr"
    access = globals()['create_'+currency+'_connection']()
    balance = access.getreceivedbyaccount(wallet_username)

    transaction = Transaction.objects.filter(
        user__username=user, currency=currency)
    if transaction:
        balance = balance - sum([Decimal(obj.amount)for obj in transaction])

    return balance


def wallet_info(currency):
    """
    Retrive all wallet info such as:
    All Users and their balance.
    Admin Wallet info.
    """
    context = {}
    access = globals()['create_'+currency+'_connection']()
    context["users"] = access.listaccounts()
    context['wallet_info'] = access.getwalletinfo()
    return context
