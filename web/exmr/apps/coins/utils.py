import json
import os
import web3
import requests
import datetime
import binascii
import subprocess


from decimal import Decimal
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


from bitcoinrpc.authproxy import AuthServiceProxy
from apps.coins.models import Wallet, WalletAddress, Coin, EthereumToken, EthereumTokenWallet,\
    Transaction, MoneroPaymentid
from apps.apiapp import views as apiview


w3 = Web3(HTTPProvider('http://35.185.10.253:8545'))


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


def create_wallet(user, currency):
    """
    create an account name in full node
    """
    erc = EthereumToken.objects.filter(contract_symbol=currency)
    if erc:
        return EthereumTokens(user=user, code=currency).generate()
    if currency in ['XRPTest']:
        return XRPTest(user).generate()
    elif currency in ['ETH']:
        return ETH(user, currency).generate()
    if currency in ['XRP']:
        return XRP(user).generate()
    elif currency in ['XMR']:
        return XMR(user, currency).generate()
    elif currency in ['DASH']:
        return globals()['create_'+currency+'_wallet'](user, currency)
    elif currency in ['BTC', 'LTC', 'XVG', 'BCH']:
        return BTC(user, currency).generate()
    elif currency in ['XLM']:
        return XLM(user, currency).generate()
    else:
        return str(currency)+' server is under maintenance'

    return addr


def get_balance(user, currency):
    """
    Retrive specified user wallet balance.
    """

    erc = EthereumToken.objects.filter(contract_symbol=currency)
    if erc:
        balance = EthereumTokens(user=user, code=currency).balance()
    elif currency == "XRPTest":
        balance = XRPTest(user).balance()
    elif currency in ["BTC", "LTC", "XVG", "BCH"]:
        balance = BTC(user, currency).balance()
    elif currency == "ETH":
        balance = ETH(user, currency).balance()
    elif currency == "XRP":
        balance = XRP(user).balance()
    elif currency == "XLM":
        balance = XLM(user, "XLM").balance()
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


class XRPTest():
    def __init__(self, user):
        self.user = user

    def balance(self):
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
            return float(Decimal(result['result']['account_data']['Balance'])/Decimal(1000000))
        except:
            return 0.0

    def send(self, destination, amount):
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

    def generate(self):
        # address_process = subprocess.Popen(
        #     ['node', '../ripple-wallet/test.js'], stdout=subprocess.PIPE)
        # address_data, err = address_process.communicate()
        # addresses = address_data.decode("utf-8") .replace("\n", "")
        # pub_address = addresses.split("{ address: '")[1].split("'")[0]
        # priv_address = addresses.split("secret: '")[-1].replace("' }", "")
        coin = Coin.objects.get(code='XRPTest')
        addresses = json.loads(requests.post(
            "https://faucet.altnet.rippletest.net/accounts").text)
        pub_address = addresses["account"]["address"]
        priv_address = addresses["account"]["secret"]
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


class ETH():
    def __init__(self, user, currency):
        self.user = user

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

    def generate(self):
        coin = Coin.objects.get(code='ETH')
        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=coin)
        if created:
            address = self.get_results("personal_newAccount", [
                                       "passphrase"])["result"]
            wallet.addresses.add(WalletAddress.objects.create(address=address))
        else:
            address = wallet.addresses.all()[0].address
        return address

    def balance(self):
        user_addr = Wallet.objects.get(
            user=self.user, name__code='ETH').addresses.all()[0].address
        params = [user_addr, "latest"]
        balance = float(w3.fromWei(w3.eth.getBalance(
            Web3.toChecksumAddress(user_addr)), "ether"))
        return balance

    def send(self, to_addr, amount):
        user_addr = Wallet.objects.get(
            user=self.user, name__code='ETH').addresses.all()[0].address
        try:
            result = w3.personal.sendTransaction({"from": Web3.toChecksumAddress(user_addr), "to": Web3.toChecksumAddress(
                to_addr), "value": Web3.toWei(amount, "ether")}, passphrase="passphrase")
            return result.title().hex()
        except:
            return {"error": "insufficient funds for gas * price + value"}

    def get_transactions(self):
        data = []
        coin = Coin.objects.get(code='ETH')
        address = Wallet.objects.get(user=self.user, name=coin).addresses.all()[0].address
        try:
            result = json.loads(requests.get("http://api.etherscan.io/api?module=account&action=txlist&address="+web3.Web3.toChecksumAddress(address)+"&startblock=0&endblock=99999999&sort=asc&apikey=K6EH1VDUFQWB8H6CW8U5SUXJK3YHTJ2U7U").text)
            data = [{'transaction_from':obj["from"], 'date':int(datetime.datetime.fromtimestamp(obj["timeStamp"])),\
                 'amount':float(obj["value"])/1000000000000000000,'currency':"ETH" } for obj in result["result"] if obj['to']==address]
            for obj in result["result"]:
                if obj["to"]=="0x"+address:
                    data.append({'to': obj["to"], 'transaction_from':obj["from"], 'date':datetime.datetime.fromtimestamp(int(obj["timeStamp"])),'amount':float(obj["value"])/1000000000000000000,'currency':"ETH" })

        except:
            pass
        return data

class XMR():
    def __init__(self, user, currency):
        self.user = user

    def create_XMR_connection(self, method, params):
        url = "http://47.254.34.85:18083/json_rpc"
        headers = {'content-type': 'application/json'}
        data = {"jsonrpc": "2.0", "id": "0",
                "method": method, "params": params}
        response = requests.post(url, json=data, headers={
            'content-type': 'application/json'})
        return response.json()

    def generate(self):
        coin = Coin.objects.get(code='XMR')
        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=coin)
        paymentid = (binascii.b2a_hex(os.urandom(8))).decode()
        moneropaymentid = MoneroPaymentid.objects.create(
            user=self.user, paymentid=paymentid)
        param = {
            "payment_id": paymentid
        }
        result = self.create_XMR_connection("make_integrated_address", param)
        address = result["result"]['integrated_address']
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
            print(result)
            return 'error'


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
            print(addr)
            wallet.addresses.add(WalletAddress.objects.create(address=addr))
            wallet.save()
        else:
            pub_address = wallet.addresses.all()[0].address
    except:
        addr = "Unable to generate address"
    return addr


class EthereumTokens():
    def __init__(self, user, code):
        self.user = user
        self.code = code
        obj = EthereumToken.objects.get(contract_symbol=code)
        self.contract = w3.eth.contract(address=Web3.toChecksumAddress(obj.contract_address),
                                        abi=obj.contract_abi)

    def generate(self):
        coin = EthereumToken.objects.get(contract_symbol=self.code)
        wallet, created = EthereumTokenWallet.objects.get_or_create(
            user=self.user, name=coin)
        if created:
            address = w3.personal.newAccount("passphrase")
            if address:
                wallet.addresses.add(
                    WalletAddress.objects.create(address=address))
        else:
            address = wallet.addresses.all()[0].address
        return address

    def balance(self):
        user_addr = EthereumTokenWallet.objects.get(
            user=self.user, name__contract_symbol=self.code).addresses.all()[0].address
        #balance = w3.fromWei(w3.eth.getBalance(w3.toChecksumAddress(user_addr)),"ether")
        balance = float(self.contract.call().balanceOf(
            Web3.toChecksumAddress(user_addr))/pow(10, self.contract.call().decimals()))
        return balance

    def send(self, to_addr, amount):
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


class BTC():
    def __init__(self, user, currency):
        self.user = user
        self.currency = currency
        self.coin = Coin.objects.get(code=currency)
        self.access = globals()['create_' + currency+'_connection']()

    def send(self, address, amount):
        valid = self.access.sendtoaddress(address, amount)
        return valid

    def balance(self):
        wallet_username = self.user.username + "_exmr"
        balance = self.access.getreceivedbyaccount(wallet_username)
        transaction = Transaction.objects.filter(
            user__username=self.user, currency=self.currency)
        if transaction:
            balance = balance - sum([Decimal(obj.amount)
                                     for obj in transaction])
        return float(balance)

    def generate(self):
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
        return addr

    def get_transactions(self):
        result = self.access.listtransactions(self.user.username+"_exmr")
        data = [{'transaction_from':obj["address"], 'date':datetime.datetime.fromtimestamp(obj["blocktime"]),\
                 'amount':float(obj["amount"]),'currency':"BTC" } for obj in result if obj['category']=='receive']
        return data


class LTC():
    def __init__(self, user, currency):
        self.temp = BTC(user, currency)

    def send(self, address, amount):
        self.temp.send(address, amount)

    def balance(self):
        self.temp.balance()

    def generate(self):
        self.temp.balance()

    def get_transactions(self):
        self.temp.get_transactions()


class XMR():
    def __init__(self, user, currency):
        self.user = user

    def create_XMR_connection(self, method, params):
        url = "http://47.254.34.85:18083/json_rpc"
        headers = {'content-type': 'application/json'}
        data = {"jsonrpc": "2.0", "id": "0",
                "method": method, "params": params}
        response = requests.post(url, json=data, headers={
            'content-type': 'application/json'})
        return response.json()

    def generate(self):
        coin = Coin.objects.get(code='XMR')
        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=coin)
        paymentid = (binascii.b2a_hex(os.urandom(8))).decode()
        moneropaymentid = MoneroPaymentid.objects.create(
            user=self.user, paymentid=paymentid)
        param = {
            "payment_id": paymentid
        }
        result = self.create_XMR_connection("make_integrated_address", param)
        address = result["result"]['integrated_address']
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
            print(result)
            return 'error'


class XRP():
    def __init__(self, user):
        self.user = user

    def balance(self):
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

    def generate(self):
        coin = Coin.objects.get(code='XRP')
        address_process = subprocess.Popen(
            ['node', '../ripple-wallet/ripple.js'], stdout=subprocess.PIPE)
        address_data, err = address_process.communicate()
        addresses = address_data.decode("utf-8") .replace("\n", "")
        pub_address = addresses.split("{ address: '")[1].split("'")[0]
        priv_address = addresses.split("secret: '")[-1].replace("' }", "")
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
    def __init__(self, user, currency):
        self.user = user
        self.currency = currency
        self.coin = Coin.objects.get(code=currency)

    def generate(self):
        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=self.coin)
        if created:
            kp = Keypair.random()
            address = kp.address().decode()
            # requests.get('https://friendbot.stellar.org/?addr=' + address)
            wallet.addresses.add(WalletAddress.objects.create(address=address))
            wallet.private = kp.seed().decode()
            wallet.save()
        else:
            address = wallet.addresses.all()[0].address
            # requests.get('https://friendbot.stellar.org/?addr=' + address)
        return address

    def balance(self):
        user_addr = Wallet.objects.get(
            user=self.user, name=self.coin).addresses.all()[0].address
        address = Address(address=user_addr)
        try:
            address.get()
            return float(Decimal(address.balances[0]['balance']))
        except:
            return 0.0

    def send(self, destination, amount):
        wallet = Wallet.objects.get(user=self.user, name=self.coin)
        try:
            builder = Builder(secret=wallet.private)
            builder.add_text_memo("EXMR, Stellar!").append_payment_op(
                destination=destination, amount=str(amount), asset_code='XLM')
            builder.sign()
            response = builder.submit()
            return response["hash"]
        except:
            return {"error": "insufficient funds"}


def get_deposit_transactions(user):
    # erc = EthereumToken.objects.filter(contract_symbol=currency)
    # if erc:
    #     return EthereumTokens(user=user, code=currency).generate()
    data = []
    wallets = Wallet.objects.filter(user=user)
    for wallet in wallets:
        if wallet.name.code == 'BTC':
            data = data + BTC(user, wallet.name.code).get_transactions()
        elif wallet.name.code == 'ETH':
            data = data + ETH(user, wallet.name.code).get_transactions()
    return data
    # if currency in ['XRPTest']:
    #     return XRPTest(user).generate()
    # elif currency in ['ETH']:
    #     return ETH(user, currency).generate()
    # if currency in ['XRP']:
    #     return XRP(user).generate()
    # elif currency in ['XMR']:
    #     return XMR(user, currency).generate()
    # elif currency in ['DASH']:
    #     return globals()['create_'+currency+'_wallet'](user, currency)
    # elif currency in ['BTC', 'LTC', 'XVG', 'BCH']:
    #     return BTC(user, currency).generate()
    # elif currency in ['XLM']:
    #     return XLM(user, currency).generate()
    # else:
    #     return str(currency)+' server is under maintenance'

# def get_token_transactions(user):
