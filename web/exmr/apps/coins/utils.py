import json
import os
import web3
import requests
import datetime
import binascii
import subprocess
import collections


from decimal import Decimal
from itertools import chain
from solc import compile_source
from web3.contract import ConciseContract
from web3 import Web3, HTTPProvider, TestRPCProvider
from stellar_base.asset import Asset
from stellar_base.memo import TextMemo
from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.operation import CreateAccount, Payment
from stellar_base.horizon import horizon_livenet, horizon_testnet
from stellar_base.transaction_envelope import TransactionEnvelope as Te
from stellar_base.builder import Builder

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from bitcoinrpc.authproxy import AuthServiceProxy
from apps.coins.models import Wallet, WalletAddress, Coin, EthereumToken, EthereumTokenWallet,\
    Transaction, MoneroPaymentid, PaybyName, TradeCommision
from apps.apiapp import views as apiview

from apps.merchant_tools.models import MerchantPaymentWallet

w3 = Web3(HTTPProvider('http://35.185.10.253:8545'))

def check_exmr_bal(cur_user, input_cur, amount):
    rates = cache.get('rates')
    try:
        exmr_rate = rates['EXMR']
    except:
        exmr_rate = 0.017
    cur_rate = rates[input_cur]
    cur_cost = amount * cur_rate
    tradecommission_obj =  TradeCommision.objects.all().first()
    trans_charge_type = tradecommission_obj.transaction_commission_type
    if trans_charge_type == "FLAT":
        exmr_amount = float(tradecommission_obj.commission_flat_rate)
    else:
        transaction_charge_usd = float(tradecommission_obj.commission_percentage) * cur_cost
        exmr_amount = transaction_charge_usd/exmr_rate
    
    user_addr = EthereumTokenWallet.objects.get(
        user=cur_user, name__contract_symbol="EXMR").addresses.all()[0].address
    current_balance = get_balance(cur_user, 'EXMR')
    if current_balance > exmr_amount:
        return True
    else:
        return False


def add_commission(cur_user,input_cur, amount):
    rates = cache.get('rates')
    try:
        exmr_rate = rates['EXMR']
    except:
        exmr_rate = 0.017

    cur_rate = rates[input_cur]
    cur_cost = amount * cur_rate
    tradecommission_obj =  TradeCommision.objects.all().first()
    trans_charge_type = tradecommission_obj.transaction_commission_type

    if trans_charge_type == "FLAT":
        exmr_amount = float(tradecommission_obj.commission_flat_rate)
    else:
        transaction_charge_usd = float(tradecommission_obj.commission_percentage) * cur_cost
        exmr_amount = transaction_charge_usd/exmr_rate
    
    admin_user = User.objects.get(is_superuser = True, username="admin")
    to_addr = EthereumTokenWallet.objects.get(user=admin_user)

    user_addr = EthereumTokenWallet.objects.get(
        user=cur_user, name__contract_symbol="EXMR").addresses.all()[0].address

    obj = EthereumToken.objects.get(contract_symbol="EXMR")
    this_contract = w3.eth.contract(address=Web3.toChecksumAddress(obj.contract_address),
                                        abi=obj.contract_abi)
    amt = int(exmr_amount)*pow(10, this_contract.call().decimals())
    w3.personal.unlockAccount(user_addr, "passphrase")
    try:
        tx_id = this_contract.transact({"from": Web3.toChecksumAddress(
            user_addr)}).transfer(Web3.toChecksumAddress(to_addr), amt)
        return tx_id.title().hex()
    except:
        return {"error": "insufficient funds for gas * price + value"}




def create_BTC_connection():
    """
    create connetion to bitcoin fullnode
    """
    access = AuthServiceProxy(
        "http://exmr:MKDNdksjfDNsjkN@35.185.10.253:8332")
    return access


def create_LTC_connection():
    """
    create connetion to litecoin fullnode
    """
    access = AuthServiceProxy("http://litecoinrpc:12345678@47.88.59.35:2300")
    return access


def create_XVG_connection():
    """
    create connetion to litecoin fullnode
    """
    access = AuthServiceProxy("http://verge:12345678@47.88.59.130:2300")
    return access


def create_BCH_connection():
    """
    create connetion to bitcoin cash fullnode
    """
    access = AuthServiceProxy(
        "http://bitcoincashrpc:12345678@39.104.231.49:2300")
    return access


def create_DASH_connection():
    return apiview.create_DASH_connection()


def create_wallet(user, currency, unique_id=None,  random=None):
    """
    create an account name in full node
    """
    erc = EthereumToken.objects.filter(contract_symbol=currency)
    if erc:
        return EthereumTokens(user=user, code=currency).generate(unique_id, random)
    if currency in ['XRPTest']:
        return XRPTest(user).generate(unique_id, random)
    elif currency in ['ETH']:
        return ETH(user, currency).generate(unique_id, random)
    if currency in ['XRP']:
        return XRP(user).generate(unique_id, random)
    elif currency in ['XMR']:
        return XMR(user, currency).generate(unique_id, random)
    elif currency in ['DASH']:
        return globals()['create_'+currency+'_wallet'](user, currency)
    elif currency in ['BTC', 'LTC', 'XVG', 'BCH']:
        return BTC(user, currency).generate(unique_id, random)
    elif currency in ['XLM']:
        return XLM(user, currency).generate(unique_id, random)
    else:
        return str(currency)+' server is under maintenance'


def get_balance(user, currency, addr=None):
    """
    Retrive specified user wallet balance.
    """
    erc = EthereumToken.objects.filter(contract_symbol=currency)
    if erc:
        balance = EthereumTokens(user=user, code=currency, addr=addr).balance()
        # balance = 1
    elif currency == "XRPTest":
        balance = XRPTest(user, addr=addr).balance()
        # balance = 1
    elif currency in ["BTC", "LTC", "XVG", "BCH"]:
        balance = BTC(user, currency, addr=addr).balance()
        # balance = 1
    elif currency == "ETH":
        balance = ETH(user, currency, addr=addr).balance()
        # balance = 1
    elif currency == "XRP":
        balance = XRP(user, addr=addr).balance()
        # balance = 1
    elif currency == "XLM":
        balance = XLM(user, "XLM", addr=addr).balance()
        # balance = 1
    elif currency == "XMR":
        balance = XLM(user, "XMR", addr=addr).balance()
        # balance = 1
    else:
        balance = 0

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


def reorder_tx_data(data):
    result = []
    for item in data:
        temp = collections.OrderedDict()
        temp['date'] = item['date']
        temp['transaction_from'] = item['transaction_from']
        temp['tx_id'] = item['tx_id']
        temp['currency'] = item['currency']
        temp['amount'] = item['amount']
        result.append(temp)
    return result


class XRPTest():
    def __init__(self, user, addr=None):
        self.user = user
        self.address = addr

    def balance(self):
        if self.address:
            params = {
                "method": "account_info",
                "params": [
                    {
                        "account": self.address,
                        "strict": True,
                        "ledger_index": "validated"
                    }
                ]
            }
            result = json.loads(requests.post(
                "https://s.altnet.rippletest.net:51234", json=params).text)
            try:
                return float(Decimal(result['result']['account_data']['Balance'])/Decimal(1000000))
            except:
                return 0.0
        else:
            wallet = Wallet.objects.get(user=self.user, name__code="XRPTest")
            secret = wallet.private
            address = wallet.addresses.all().first().address
            params = {
                "method": "account_info",
                "params": [
                    {
                        "account": address,
                        "strict": True,
                        "ledger_index": "validated"
                    }
                ]
            }
        result = json.loads(requests.post(
            "https://s.altnet.rippletest.net:51234", json=params).text)
        try:
            return (float(Decimal(result['result']['account_data']['Balance'])/Decimal(1000000))-0)
        except:
            return 0.0

    def send(self, destination, amount):
        destination = check_pay_by_name(destination, "XRPTest")
        wallet = Wallet.objects.get(user=self.user, name__code="XRPTest")
        secret = wallet.private
        address = wallet.addresses.all().first().address
        params = {"method": "sign",
                  "params": [
                      {
                          "secret": secret,
                          "tx_json": {
                              "TransactionType": "Payment",
                              "Account": address,
                              "Amount": str(int(amount)*1000000),
                              "Destination": destination
                          }
                      }
                  ]
                  }
        result = json.loads(requests.post(
            "https://s.altnet.rippletest.net:51234", json=params).text)
        params = {
            "method": "submit",
            "params": [
                {
                    "tx_blob": result['result']['tx_blob']
                }
            ]
        }
        submit = json.loads(requests.post(
            "https://s.altnet.rippletest.net:51234", json=params).text)
        try:
            return result['result']['tx_json']['hash']
        except:
            return result['result']['error']

    def generate(self, unique_id, random=None):
        coin = Coin.objects.get(code='XRPTest')
        addresses = json.loads(requests.post(
            "https://faucet.altnet.rippletest.net/accounts").text)
        pub_address = addresses["account"]["address"]
        priv_address = addresses["account"]["secret"]
        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=coin)

        if random:
            MerchantPaymentWallet.objects.create(
                merchant=self.user, address=pub_address, private=priv_address, code="XRPTest", unique_id=unique_id)
            return pub_address

        if created:
            wallet.addresses.add(
                WalletAddress.objects.create(address=pub_address))
            wallet.private = priv_address
            wallet.save()
        else:
            pub_address = wallet.addresses.all()[0].address
        return pub_address

class ETH():
    def __init__(self, user=None, currency="ETH", addr=None):
        self.user = user
        self.address = addr
        self.currency = currency

    def get_results(self, method, params):
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        serialized_data = json.dumps(message)
        headers = {'Content-type': 'application/json'}
        response = requests.post(
            "http://35.185.10.253:8545", headers=headers, data=serialized_data)
        return response.json()

    def generate(self, unique_id, random=None):
        coin = Coin.objects.get(code='ETH')
        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=coin)
        address = self.get_results("personal_newAccount", [
                                   "passphrase"])["result"]
        wallet.addresses.add(WalletAddress.objects.create(address=address))
        # if created:
        #     address = self.get_results("personal_newAccount", [
        #                                "passphrase"])["result"]
        #     wallet.addresses.add(WalletAddress.objects.create(address=address))
        # else:
        #     address = wallet.addresses.all()[0].address
        if random:
            address = self.get_results("personal_newAccount", [
                                       "passphrase"])["result"]
            MerchantPaymentWallet.objects.create(
                merchant=self.user, address=address, unique_id=unique_id, code="ETH")
            return address
        return address

    def balance(self):
        current_balance = 0
        try:
            user_addr_list = Wallet.objects.get(user=self.user, name__code='ETH').addresses.all()
            current_balance = 0
            for temp_addr in user_addr_list:
                balance = float(w3.fromWei(w3.eth.getBalance(Web3.toChecksumAddress(temp_addr.address)), "ether"))
                current_balance = current_balance + balance
            return current_balance
        except:
            return current_balance

    def send(self, to_addr, amount):
        min_transaction_fee = float((Coin.objects.get(code='ETH')).min_transaction_fees)
        amount = float(amount)
        to_addr = check_pay_by_name(to_addr, "ETH")
        user_addr = Wallet.objects.get(user=self.user, name__code='ETH').addresses.all()[0].address
        user_addr_list = (Wallet.objects.get(
            user=self.user, name__code='ETH')).addresses.all()
        current_balance = 0
        temp_addr_list = {}

        addr_balance_list = {}
        for temp_addr in user_addr_list:
            try:
                addr_balance_list[temp_addr.address] = (cache.get(temp_addr.address) - min_transaction_fee)
            except:
                addr_balance_list[temp_addr.address] = (self.rcvd_bal(temp_addr.address)) - min_transaction_fee

        sorted_addr_balance_list = sorted(addr_balance_list.items(), key=lambda kv: kv[1], reverse=True)
        temp_bal_amt = amount
        cur_addr_list ={}
        for addr_temp, addr_bal in sorted_addr_balance_list:
            if temp_bal_amt > 0:
                if temp_bal_amt > addr_bal:
                    temp_bal_amt = temp_bal_amt - addr_bal
                    cur_addr_list[addr_temp]= addr_bal
                else:
                    cur_addr_list[addr_temp] = temp_bal_amt
                    temp_bal_amt = 0
            else:
                break
        if temp_bal_amt > 0:
            return {"error": "insufficient funds for gas * price + value"}
            
        result_hex_list = []
        try:
            for addr_temp, addr_bal in cur_addr_list.items():
                result = w3.personal.sendTransaction({"from": Web3.toChecksumAddress(addr_temp), "to": Web3.toChecksumAddress(
                    to_addr), "value": Web3.toWei(addr_bal, "ether")}, passphrase="passphrase")
                result_hex_list.append(result.title().hex())
            sending_commission = add_commission(self.user, self.currency, amount)
            return result_hex_list
        except:
            return {"error": "insufficient funds for gas * price + value"}

    def get_transactions(self):
        data = []
        coin = Coin.objects.get(code='ETH')
        address = Wallet.objects.get(
            user=self.user, name=coin).addresses.all()[0].address
        try:
            result = json.loads(requests.get("http://api.etherscan.io/api?module=account&action=txlist&address="+web3.Web3.toChecksumAddress(
                address)+"&startblock=0&endblock=99999999&sort=asc&apikey=K6EH1VDUFQWB8H6CW8U5SUXJK3YHTJ2U7U").text)
            data = [{'transaction_from': obj["from"], 'date':int(datetime.datetime.fromtimestamp(obj["timeStamp"])),
                     'amount':float(obj["value"])/1000000000000000000, 'currency':"ETH"} for obj in result["result"] if obj['to'] == address]
            for obj in result["result"]:
                if obj["to"] == "0x"+address:
                    data.append({'to': obj["to"], 'tx_id': obj["hash"], 'transaction_from': obj["from"], 'date': datetime.datetime.fromtimestamp(
                        int(obj["timeStamp"])), 'amount': float(obj["value"])/1000000000000000000, 'currency': "ETH"})

        except:
            pass
        return data

    def rcvd_bal(self, address):
        try:
            balance = float(w3.fromWei(w3.eth.getBalance(
                Web3.toChecksumAddress(addresses)), "ether"))
        except:
            balance = 0
        return float(balance)


def create_DASH_wallet(user, currency):
    coin = Coin.objects.get(code=currency)
    wallet_username = user.username + "_exmr"
    try:
        addr = apiview.createaddr(wallet_username, coin)
        # addr = False
        # raise Exception
    except:
        return ''
    try:
        wallet, created = Wallet.objects.get_or_create(user=user, name=coin)
        if created:
            wallet.addresses.add(WalletAddress.objects.create(address=addr))
            wallet.save()
        else:
            pub_address = wallet.addresses.all()[0].address
    except:
        addr = "Unable to generate address"
    return addr


class EthereumTokens():
    def __init__(self, user, code, addr=None):
        self.user = user
        self.code = code
        obj = EthereumToken.objects.get(contract_symbol=code)
        self.contract = w3.eth.contract(address=Web3.toChecksumAddress(obj.contract_address),
                                        abi=obj.contract_abi)
        self.address = addr

    def get_results(self, method, params):
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        serialized_data = json.dumps(message)
        headers = {'Content-type': 'application/json'}
        response = requests.post(
            "http://35.185.10.253:8545", headers=headers, data=serialized_data)
        return response.json()

    
    def generate(self, unique_id, random=None):
        coin = EthereumToken.objects.get(contract_symbol=self.code)
        try:
            wallet, created = Wallet.objects.get_or_create(
                user=self.user, name=coin)
        except:
            wallet, created = Wallet.objects.get_or_create(
                user=self.user, token_name=coin)

        address = self.get_results("personal_newAccount", [
                                   "passphrase"])["result"]
        wallet.addresses.add(WalletAddress.objects.create(address=address))

        if random:
            MerchantPaymentWallet.objects.create(
                merchant=self.user, address=address, code=self.code, unique_id=unique_id)
            return address

        return address

    def balance(self, address=None):
        coin = EthereumToken.objects.get(contract_symbol=self.code)
        if self.address:
            user_addr = address
            balance = float(self.contract.call().balanceOf(
                Web3.toChecksumAddress(user_addr))/pow(10, self.contract.call().decimals()))
        else:
            try:
                user_addr_list_3 = EthereumTokenWallet.objects.get(user=self.user, name__contract_symbol=self.code).addresses.all()
            except:
                user_addr_list_3 = []

            user_addr_list_1 = Wallet.objects.get(
                user=self.user, token_name=coin).addresses.all()
            ETHcoin = Coin.objects.get(code='ETH')
            user_addr_list_2 = Wallet.objects.get(user=self.user, name=ETHcoin).addresses.all()
            user_addr_list = list(chain(user_addr_list_1, user_addr_list_2, user_addr_list_3))
            balance = 0
            for temp_addr in user_addr_list:
                user_addr = temp_addr.address
                balance =balance + float(self.contract.call().balanceOf(
                    Web3.toChecksumAddress(user_addr))/pow(10, self.contract.call().decimals()))
        return balance

    def send(self, to_addr, amount):
        to_addr = check_pay_by_name(to_addr, "ETH")
        if '$' in to_addr:
            to_user = PaybyName.objects.get(label=to_user.strip('$')).user
            to_addr = EthereumTokenWallet.objects.get(
                user=to_user, name__contract_symbol=self.code).addresses.all()[0].address

        user_addr = EthereumTokenWallet.objects.get(
            user=self.user, name__contract_symbol=self.code).addresses.all()[0].address
        amt = int(amount)*pow(10, self.contract.call().decimals())
        w3.personal.unlockAccount(user_addr, "passphrase")
        try:
            tx_id = self.contract.transact({"from": Web3.toChecksumAddress(
                user_addr)}).transfer(Web3.toChecksumAddress(to_addr), amt)
            return tx_id.title().hex()
        except:
            return {"error": "insufficient funds for gas * price + value"}

    def get_transactions(self):
        data = []
        coin = Coin.objects.get(code='ETH')
        address = Wallet.objects.get(
            user=self.user, name=coin).addresses.all()[0].address
        try:
            result = json.loads(requests.get("http://api.etherscan.io/api?module=account&action=tokentx&address="+web3.Web3.toChecksumAddress(
                address)+"&startblock=0&endblock=99999999&sort=asc&apikey=K6EH1VDUFQWB8H6CW8U5SUXJK3YHTJ2U7U").text)
            data = [{'transaction_from': obj["from"], 'date':int(datetime.datetime.fromtimestamp(obj["timeStamp"])),
                     'amount':float(obj["value"])/1000000000000000000, 'currency':"ETH"} for obj in result["result"] if obj['to'] == address]
            for obj in result["result"]:
                if obj["to"] == "0x"+address and self.code == obj["tokenSymbol"]:
                    data.append({'to': obj["to"], 'tx_id': obj["hash"], 'transaction_from': obj["from"], 'date': datetime.datetime.fromtimestamp(
                        int(obj["timeStamp"])), 'amount': float(obj["value"])/1000000000000000000, 'currency': "ETH"})

        except:
            pass
        return data


class BTC:
    def __init__(self, user=None, currency='BTC', addr=None):
        self.user = user
        self.currency = currency
        self.coin = Coin.objects.get(code=currency)
        self.access = globals()['create_' + currency+'_connection']()
        self.address = addr

    def send(self, address, amount):
        address = check_pay_by_name(address, self.currency)
        valid = self.access.sendtoaddress(address, amount)
        return valid

    def balance(self):
        if not self.address:
            wallet_username = self.user.username + "_exmr"
            balance = self.access.getreceivedbyaccount(wallet_username)
            transaction = Transaction.objects.filter(
                user__username=self.user, currency=self.currency)
            if transaction:
                balance = balance - sum([Decimal(obj.amount)
                                         for obj in transaction])
        else:
            balance = self.access.getreceivedbyaddress(self.address)

        return float(balance)

    def generate(self, unique_id, random=None):
        coin = Coin.objects.get(code=self.currency)
        wallet_username = self.user.username + "_exmr"
        access = globals()['create_'+self.currency+'_connection']()
        try:
            addr = access.getnewaddress(wallet_username)
            wallet, created = Wallet.objects.get_or_create(
                user=self.user, name=coin)
            wallet.addresses.add(WalletAddress.objects.create(address=addr))
        except:
            addr = ''
        if random:
            MerchantPaymentWallet.objects.create(
                merchant=self.user, address=addr, code=self.currency, unique_id=unique_id)
            return addr
        return addr

    def get_transactions(self):
        result = self.access.listtransactions(self.user.username+"_exmr")
        data = [{'transaction_from': obj["address"], 'tx_id':obj["txid"], 'date':datetime.datetime.fromtimestamp(obj["blocktime"]),
                 'amount':float(obj["amount"]), 'currency': self.currency} for obj in result if obj['category'] == 'receive']
        return data

    def rcvd_bal(self, address):
        try:
            balance = self.access.getreceivedbyaddress(address)
        except:
            balance = 0
        return float(balance)


class LTC():
    def __init__(self, user, currency, addr=None):
        self.temp = BTC(user, currency)
        self.address = addr

    def send(self, address, amount):
        self.temp.send(address, amount)

    def balance(self):
        self.temp.balance(self.address)

    def generate(self, random=None):
        self.temp.balance()

    def get_transactions(self):
        self.temp.get_transactions()


class XMR():
    def __init__(self, user, currency, addr=None):
        self.user = user
        self.address = addr

    def create_XMR_connection(self, method, params):
        url = "http://47.254.34.85:18083/json_rpc"
        headers = {'content-type': 'application/json'}
        data = {"jsonrpc": "2.0", "id": "0",
                "method": method, "params": params}
        response = requests.post(url, json=data, headers={
            'content-type': 'application/json'})
        return response.json()

    def generate(self, unique_id, random=None):
        coin = Coin.objects.get(code='XMR')
        paymentid = (binascii.b2a_hex(os.urandom(8))).decode()
        moneropaymentid = MoneroPaymentid.objects.create(
            user=self.user, paymentid=paymentid)
        param = {
            "payment_id": paymentid
        }
        result = self.create_XMR_connection("make_integrated_address", param)
        address = result["result"]['integrated_address']
        if random:
            MerchantPaymentWallet.objects.create(
                merchant=self.user, address=address, unique_id=unique_id, code="XMR")
            return address

        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=coin)
        wallet.addresses.add(WalletAddress.objects.create(address=address))
        return address

    def balance(self):
        coin = Coin.objects.get(code='XMR')
        wallet = Wallet.objects.get(user=self.user, name=coin)
        if wallet:
            temp_list = MoneroPaymentid.objects.filter(user=self.user)
            balance = 0
            for pids in temp_list:
                param = {
                    "payment_id": pids.paymentid
                }
                try:
                    temp_balance = self.create_xmr_connection("get_payments", param)[
                        "result"]['payments'][0]['amount']
                except:
                    temp_balance = 0
                balance = balance + temp_balance
        else:
            balance = 0
        return balance

    def send(self, destination, amount):
        destination = check_pay_by_name(destination, "XMR")
        coin = Coin.objects.get(code='XMR')
        wallet = Wallet.objects.get(user=self.user, name=coin)
        param = {
            "destinations": [
                {
                    "amount": amount,
                    "address": destination
                }
            ],
            "mixin": 4,
            "get_tx_key": True
        }
        result = self.create_XMR_connection("transfer", param)
        try:
            return result['result']['tx_hash']
        except:
            return 'error'


class XRP():
    def __init__(self, user, addr=None):
        self.user = user
        self.address = addr

    def balance(self):
        if self.address:
            params = {
                "method": "account_info",
                "params": [
                    {
                        "account": self.address,
                        "strict": True,
                        "ledger_index": "validated"
                    }
                ]
            }
            result = json.loads(requests.post(
                "http://s1.ripple.com:51234/", json=params).text)
            try:
                return float(Decimal(result['result']['account_data']['Balance'])/Decimal(1000000))
            except:
                return 0.0
        else:
            wallet = Wallet.objects.get(user=self.user, name__code="XRP")
            secret = wallet.private
            address = wallet.addresses.all().first().address
            params = {
                "method": "account_info",
                "params": [
                    {
                        "account": address,
                        "strict": True,
                        "ledger_index": "validated"
                    }
                ]
            }
            result = json.loads(requests.post(
                "http://s1.ripple.com:51234/", json=params).text)
            try:
                return float(Decimal(result['result']['account_data']['Balance'])/Decimal(1000000))
            except:
                return 0.0

    def send(self, destination, amount):
        destination = check_pay_by_name(destination, "XRP")
        wallet = Wallet.objects.get(user=self.user, name__code="XRP")
        secret = wallet.private
        address = wallet.addresses.all().first().address
        params = {"method": "sign",
                  "params": [
                      {
                          "secret": secret,
                          "tx_json": {
                              "TransactionType": "Payment",
                              "Account": address,
                              "Amount": str(float(amount)*1000000),
                              "Destination": destination
                          }
                      }
                  ]
                  }
        result = json.loads(requests.post(
            "http://35.185.10.253:5005/", json=params).text)
        params = {
            "method": "submit",
            "params": [
                {
                    "tx_blob": result['result']['tx_blob']
                }
            ]
        }
        submit = json.loads(requests.post(
            "http://35.185.10.253:5005/", json=params).text)
        try:
            return result['result']['tx_json']['hash']
        except:
            return result['result']['error_message']

    def generate(self, unique_id, random=None):
        coin = Coin.objects.get(code='XRP')
        address_process = subprocess.Popen(
            ['node', '../ripple-wallet/ripple.js'], stdout=subprocess.PIPE)
        address_data, err = address_process.communicate()
        addresses = address_data.decode("utf-8") .replace("\n", "")
        pub_address = addresses.split("{ address: '")[1].split("'")[0]
        priv_address = addresses.split("secret: '")[-1].replace("' }", "")

        if random:
            MerchantPaymentWallet.objects.create(
                merchant=self.user, address=pub_address, private=priv_address, unique_id=unique_id, code="XRP")
            return pub_address

        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=coin)
        if created:
            wallet.addresses.add(
                WalletAddress.objects.create(address=pub_address))
            wallet.private = priv_address
            wallet.save()
        else:
            pub_address = wallet.addresses.all()[0].address
        return pub_address


def create_transaction(user, currency, amount, address):
    if currency in ['BTC', 'LTC']:
        currency = Coin.objects.get(code=currency)
        try:
            wallet_username = user.username + "_exmr"
        except:
            wallet_username = user + "_exmr"
        access = globals()['create_'+currency+'_connection']()
        valid = access.sendtoaddress(address, amount)
    elif currency == "eth":
        valid = ETH.send(self.request.user, amount, address)


def get_primary_address(user, currency):
    erc = EthereumToken.objects.filter(contract_symbol=currency)
    if erc:
        return EthereumTokens(user=user, code=currency).create_erc_wallet()
    if currency in ['XRPTest']:
        return XRP(user).create_xrp_wallet()
    if currency in ['ETH']:
        return ETH(user, currency).generate()
    elif currency in ['DASH']:
        return globals()['create_'+currency+'_wallet'](user, currency)
    elif currency in ['BTC', 'LTC']:
        coin = Coin.objects.get(code=currency)
        try:
            wallet = Wallet.objects.get(user=user, name=coin)
            addr = wallet.addresses.all()[0].address
        except:
            return create_wallet(user, currency)
        return addr

    else:
        return str(currency)+' server is under maintenance'

    return addr


class XLM():
    def __init__(self, user=None, currency="XLM", addr=None):
        self.user = user
        self.currency = currency
        self.coin = Coin.objects.get(code=currency)
        self.address = addr

    def generate(self, unique_id, random=None):
        kp = Keypair.random()
        address = kp.address().decode()
        if random:
            MerchantPaymentWallet.objects.create(merchant=self.user, address=address, private=kp.seed(
            ).decode(), unique_id=unique_id, code=self.currency)
            return address

        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=self.coin)
        if created:
            # requests.get('https://friendbot.stellar.org/?addr=' + address)
            wallet.addresses.add(WalletAddress.objects.create(address=address))
            wallet.private = kp.seed().decode()
            wallet.save()
        else:
            address = wallet.addresses.all()[0].address
            # requests.get('https://friendbot.stellar.org/?addr=' + address)
        return address

    def balance(self, address=None):
        if address:
            addr = Address(address=address)
            try:
                addr.get()
                return float(Decimal(addr.balances[0]['balance']))
            except:
                return 0.0
        else:
            user_addr = Wallet.objects.get(
                user=self.user, name=self.coin).addresses.all()[0].address
            address = Address(address=user_addr)
            try:
                address.get()
                return float(Decimal(address.balances[0]['balance']))
            except:
                return 0.0

    def send(self, destination, amount):
        destination = check_pay_by_name(destination, "XLM")
        wallet = Wallet.objects.get(user=self.user, name=self.coin)
        try:
            builder = Builder(secret=wallet.private)
            builder.add_text_memo("EXMR, Stellar!").append_payment_op(
                destination=destination.strip(), amount=str(amount), asset_code='XLM')
            builder.sign()
            response = builder.submit()
            return response["hash"]
        except:
            return {"error": "insufficient funds"}


class DepositTransaction():

    def __init__(self, user):
        self.user = user

    def get_deposit_transactions(self):
        data = []
        wallets = Wallet.objects.filter(user=self.user)
        available_coins = Coin.objects.filter(active=True, display=True)
        for wallet in wallets:
            if wallet.name in available_coins:
                data = data + self.get_currency_txn(wallet.name.code)
        return data

    def get_currency_txn(self, currency):
        erc = EthereumToken.objects.filter(contract_symbol=currency)
        if erc:
            return EthereumTokens(user=self.user, code=currency).get_transactions()
        if currency in ['BTC', 'LTC', 'XVG', 'BCH']:
            return BTC(self.user, currency).get_transactions()
        elif currency == 'ETH':
            return ETH(self.user, currency).get_transactions()
        else:
            return []


def check_pay_by_name(name, currency):
    if '$' in name:
        try:
            user = PaybyName.objects.get(label=name.strip('$')).user
            wallet = Wallet.objects.get(user=user, name__code=currency)
            return wallet.addresses.all().first().address
        except:
            pass
    return name
