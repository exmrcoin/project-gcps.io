import json
import web3
import requests

from decimal import Decimal
from solc import compile_source
from web3.contract import ConciseContract
from web3 import Web3, HTTPProvider, TestRPCProvider


from bitcoinrpc.authproxy import AuthServiceProxy
from apps.coins.models import Wallet, WalletAddress, Coin, EthereumToken, EthereumTokenWallet
from apps.apiapp import views as apiview


w3 = Web3(HTTPProvider('http://35.237.231.141:8545'))

def create_BTC_connection():
    """
    create connetion to bitcoin fullnode
    """
    access = AuthServiceProxy("http://exmr:MKDNdksjfDNsjkN@35.237.231.141:8332")
    return access


def create_LTC_connection():
    """
    create connetion to litecoin fullnode
    """
    access = AuthServiceProxy("http://anand:anandkrishnan@18.218.176.0:19332")
    return access


def create_BCH_connection():
    """
    create connetion to bitcoin cash fullnode
    """
    access = AuthServiceProxy("http://anand:anandkrishnan@13.58.70.247:18332")
    return access

def create_DASH_connection():
    return apiview.create_DASH_connection()


def create_wallet(user, currency):
    """
    create an account name in full node
    """
    erc = EthereumToken.objects.filter(contract_symbol=currency)
    if erc:
        return EthereumTokens(user=user, code=currency).create_erc_wallet()
    if currency in ['XRPTest']:
        return XRP(user).create_xrp_wallet()
    if currency in ['ETH']:
        return Eth(user).create_eth_wallet()
    elif currency in ['DASH']:
        return globals()['create_'+currency+'_wallet'](user,currency)
    elif currency in ['BTC']:
        coin = Coin.objects.get(code=currency)
        wallet_username = user.username + "_exmr"
        access = globals()['create_'+currency+'_connection']()
        print(access)
        try:
            addr = access.getnewaddress(wallet_username)
            wallet, created = Wallet.objects.get_or_create(user=user, name=coin)
            wallet.addresses.add(WalletAddress.objects.create(address=addr))
        except:
            addr = ''
    
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
    if currency == "XRPTest":
        balance = XRP(user).balance()
    elif currency == "BTC":
        wallet_username = user.username + "_exmr"
        access = globals()['create_'+currency+'_connection']()
        balance = access.getreceivedbyaccount(wallet_username)

        transaction = Transaction.objects.filter(
            user__username=user, currency=currency)
        if transaction:
            balance = balance - sum([Decimal(obj.amount)for obj in transaction])
    elif currency == "ETH":
        balance = Eth(user).balance()
        # wallet_username = user.username + "_exmr"
        # access = globals()['create_'+currency+'_connection']()
        # balance = access.getreceivedbyaccount(wallet_username)

        # transaction = Transaction.objects.filter(
        #     user__username=user, currency=currency)
        # if transaction:
        #     balance = balance - sum([Decimal(obj.amount)for obj in transaction])
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



class XRP():
    def __init__(self, user):
        self.user = user

    def balance(self):
        wallet = Wallet.objects.get(user=self.user, name__code="XRPTest")
        secret = wallet.private
        address = wallet.addresses.all().first().address
        params =    {
                        "method": "account_info",
                        "params": [
                            {
                                "account": address,
                                "strict": True,
                                "ledger_index": "validated"
                            }
                        ]
                    }
        result = json.loads(requests.post("https://s.altnet.rippletest.net:51234",json=params).text)
        try:
            return Decimal(result['result']['account_data']['Balance'])/Decimal(1000000)
        except:
            return "0"

    def send(self, destination, amount):
        wallet = Wallet.objects.get(user=self.user, name__code="XRPTest")
        secret = wallet.private
        address = wallet.addresses.all().first().address
        params =    { "method" : "sign",
                      "params" : [ 
                                    { 
                                        "secret" : secret,
                                        "tx_json" : {
                                                        "TransactionType":"Payment",
                                                        "Account":address,
                                                        "Amount":str(int(amount)*1000000),
                                                        "Destination":destination
                                                    }
                                    } 
                                ] 
                    }
        result = json.loads(requests.post("https://s.altnet.rippletest.net:51234",json=params).text)
        params = {
                    "method": "submit",
                    "params": [
                        {
                            "tx_blob": result['result']['tx_blob']
                        }
                    ]
                }
        submit = json.loads(requests.post("https://s.altnet.rippletest.net:51234",json=params).text)
        try:
            return result['result']['tx_json']['hash']
        except:
            return result['result']['error']

    def create_xrp_wallet(self):
        # address_process = subprocess.Popen(
        #     ['node', '../ripple-wallet/test.js'], stdout=subprocess.PIPE)
        # address_data, err = address_process.communicate()
        # addresses = address_data.decode("utf-8") .replace("\n", "")
        # pub_address = addresses.split("{ address: '")[1].split("'")[0]
        # priv_address = addresses.split("secret: '")[-1].replace("' }", "")
        coin = Coin.objects.get(code='XRPTest')
        addresses = json.loads(requests.post("https://faucet.altnet.rippletest.net/accounts").text)
        pub_address = addresses["account"]["address"] 
        priv_address = addresses["account"]["secret"] 
        wallet, created = Wallet.objects.get_or_create(user=self.user, name=coin)
        if created:
            wallet.addresses.add(WalletAddress.objects.create(address=pub_address))
            wallet.private=priv_address
            wallet.save()
        else:
            pub_address = wallet.addresses.all()[0].address
        return pub_address

def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])

class Eth():
    def __init__(self, user):
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
        response = requests.post("http://35.237.231.141:8545",headers=headers, data=serialized_data)
        return response.json()

    def create_eth_wallet(self):
        coin = Coin.objects.get(code='ETH')
        wallet, created = Wallet.objects.get_or_create(user=self.user, name=coin)
        if created:
            address = self.get_results("personal_newAccount", ["passphrase"])["result"]
            wallet.addresses.add(WalletAddress.objects.create(address=address))
        else:
            address = wallet.addresses.all()[0].address
        return address

    def balance(self):
        user_addr = Wallet.objects.get(
            user=self.user, name__code='ETH').addresses.all()[0].address
        params = [user_addr, "latest"]
        balance = float(w3.fromWei(w3.eth.getBalance(Web3.toChecksumAddress(user_addr)), "ether"))
        return balance

    def send(self, to_addr, amount):
        user_addr = Wallet.objects.get(
            user=self.user, name__code='ETH').addresses.all()[0].address
        try:
            result = w3.personal.sendTransaction({"from":Web3.toChecksumAddress(user_addr), "to":Web3.toChecksumAddress(to_addr), "value": Web3.toWei(amount, "ether")},passphrase="passphrase")
            return result.title().hex()
        except:
            return {"error": "insufficient funds for gas * price + value"}
        

def create_DASH_wallet(user,currency):
    coin = Coin.objects.get(code=currency)
    wallet_username = user.username + "_exmr"
    try:
        addr = apiview.createaddr(wallet_username,coin)
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
        self.contract = w3.eth.contract(address=obj.contract_address, abi=obj.contract_abi)

    def create_erc_wallet(self):
        coin = EthereumToken.objects.get(contract_symbol=self.code)
        wallet, created = EthereumTokenWallet.objects.get_or_create(user=self.user, name=coin)
        if created:
            address = w3.personal.newAccount("passphrase")
            if address:
                wallet.addresses.add(WalletAddress.objects.create(address=address))
        else:
            address = wallet.addresses.all()[0].address
        return address

    def balance(self):
        user_addr = EthereumTokenWallet.objects.get(
            user=self.user, name__contract_symbol=self.code).addresses.all()[0].address
        #balance = w3.fromWei(w3.eth.getBalance(w3.toChecksumAddress(user_addr)),"ether")
        balance = self.contract.call().balanceOf(user_addr)/pow(10,self.contract.call().decimals())
        return balance

    def send(self, to_addr, amount):
        user_addr = EthereumTokenWallet.objects.get(
            user=self.user, name__contract_symbol=self.code).addresses.all()[0].address
        amt = int(amount)*pow(10,self.contract.call().decimals())
        w3.personal.unlockAccount(user_addr,"passphrase")
        try:
            tx_id = self.contract.transact({"from": Web3.toChecksumAddress(user_addr)}).transfer(Web3.toChecksumAddress(to_addr), amt)
            return tx_id.title().hex()
        except:
            return {"error": "insufficient funds for gas * price + value"}

class BTC():
    def __init__(self, user, currency):
        self.user = user
        self.currency = currency
        self.coin = Coin.objects.get(code=currency)

    def send(self, address, amount):
        access = getattr(apps.coins.utils, 'create_' +
                             currency+'_connection')()
        valid = access.sendtoaddress(address, amount)
        return valid
    
    def balance(self):
        balance = get_balance(self.user, self.currency)
        return balance

def create_transaction(user,currency,amount, address):
    if currency in ['BTC','LTC']:
        currency = Coin.objects.get(code=currency)
        try:
            wallet_username = user.username + "_exmr"
        except:
            wallet_username = user + "_exmr"
        access = globals()['create_'+currency+'_connection']()
        valid = access.sendtoaddress(address, amount)
    elif currency == "eth":
            valid = Eth.send(self.request.user, amount, address)


def get_primary_address(user, currency):
    erc = EthereumToken.objects.filter(contract_symbol=currency)
    if erc:
        return EthereumTokens(user=user, code=currency).create_erc_wallet()
    if currency in ['XRPTest']:
        return XRP(user).create_xrp_wallet()
    if currency in ['ETH']:
        return Eth(user).create_eth_wallet()
    elif currency in ['DASH']:
        return globals()['create_'+currency+'_wallet'](user,currency)
    elif currency in ['BTC','LTC']:
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