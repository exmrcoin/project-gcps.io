import json
import requests

from decimal import Decimal

from bitcoinrpc.authproxy import AuthServiceProxy
from apps.coins.models import Wallet, WalletAddress, Coin
from apps.apiapp import views as apiview

def create_BTC_connection():
    """
    create connetion to bitcoin fullnode
    """
    access = AuthServiceProxy("http://anand:anandkrishnan@18.218.176.0:18332")
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
    if currency in ['XRPTest']:
        return XRP(user).create_xrp_wallet()
    if currency in ['ETH']:
        return Eth(user).create_eth_wallet()
    elif currency in ['DASH']:
        return globals()['create_'+currency+'_wallet'](user,currency)
    else:
        coin = Coin.objects.get(code=currency)
        wallet_username = user.username + "_exmr"
        access = globals()['create_'+currency+'_connection']()
        print(access)
        try:
            addr = access.getnewaddress(wallet_username)
            # addr = False
            # raise Exception
        except:
            addr = ''
        wallet, created = Wallet.objects.get_or_create(user=user, name=coin)
        # wallet.addresses.add(WalletAddress.objects.create(address=addr))
    return addr


def get_balance(user, currency):
    """
    Retrive specified user wallet balance.
    """
    print (currency)
    if currency == "XRPTest":
        balance = XRP(user).balance()
    else:
        # wallet_username = user.username + "_exmr"
        # access = globals()['create_'+currency+'_connection']()
        # balance = access.getreceivedbyaccount(wallet_username)

        # transaction = Transaction.objects.filter(
        #     user__username=user, currency=currency)
        # if transaction:
        #     balance = balance - sum([Decimal(obj.amount)for obj in transaction])
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
        response = requests.post("http://35.196.180.11:8545",headers=headers, data=serialized_data)
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

    def get_eth_balance(user):
        user_addr = Wallet.objects.get(
            user=user, name='eth').addresses.all()[0].address
        params = [user_addr, "latest"]
        balance = get_results("eth_getBalance", params)['result']
        return balance

    def send_eth_transaction(self, user, amount, to_addr):
        user_addr = Wallet.objects.get(
            user=user, name='eth').addresses.all()[0].address
        params = [
            {
                "from": user_addr,
                "to": to_addr,
                "value": float_to_hex(amount)
            },
            "psalm"
        ]
        result = get_results("personal_sendTransaction", params)
        if result.get("error"):
            return {"error": result.get("error").get("message")}
        else:
            return True
def create_DASH_wallet(user,currency):
    coin = Coin.objects.get(code=currency)
    wallet_username = user.username + "_exmr"
    try:
        import pdb ; pdb.set_trace()
        addr = apiview.createaddr(wallet_username,coin)
        # addr = False
        # raise Exception
    except:
        addr = ''
    wallet, created = Wallet.objects.get_or_create(user=user, name=coin)
    if created:
        print(addr)
        wallet.addresses.add(WalletAddress.objects.create(address=addr))
        wallet.save()
    else:
        pub_address = wallet.addresses.all()[0].address
    return addr
