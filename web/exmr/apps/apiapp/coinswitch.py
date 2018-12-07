import requests

BASE_URL = "https://api.coinswitch.co/%s"

headers = {
    'x-api-key': "cRbHFJTlL6aSfZ0K2q7nj6MgV5Ih4hbA2fUG0ueO",
    'x-user-ip': "202.88.246.92"
    }

def _coinswitch_get_request(url_path):
    url = BASE_URL % url_path
    response = requests.request("GET", url, headers=headers)
    return response.json()  

def get_coins():
    return _coinswitch_get_request('v2/coins')

def get_rate(input_coin, output_coin):
    url_path = "rate/{}_{}".format(input_coin, output_coin)
    return _coinswitch_get_request(url_path)

def get_deposit_limit(input_coin, output_coin):
    url_path = "limit/{}_{}".format(input_coin, output_coin)
    return _coinswitch_get_request(url_path)

def get_market_info(input_coin, output_coin):
    url_path = "marketinfo/{}_{}".format(input_coin, output_coin)
    return _coinswitch_get_request(url_path)

def get_recent_tx_list(max_transactions):
    assert 1<= max_transactions <= 50
    url_path = "recenttx/{}".format(max_transactions)
    return _coinswitch_get_request(url_path)

def get_tx_status(address):
    url_path = "txStat/{}".format(address)
    return _coinswitch_get_request(url_path)

def get_time_remaining_on_fixed_tx(address):
    url_path = "timeremaining/{}".format(address)
    return _coinswitch_get_request(url_path)

def get_tx_by_api_key(api_key):
    url_path = "txbyapikey/{}".format(api_key)
    return _coinswitch_get_request(url_path)

def get_tx_by_address(address, api_key):
    url_path = "txbyapikey/{}/{}".format(address, api_key)
    return _coinswitch_get_request(url_path)

def validate_address(address, coin_symbol):
    url_path = "validateAddress/{}/{}".format(address, coin_symbol)
    return _coinswitch_get_request(url_path)

def _coinswitch_post_request(url_path, payload):
    url = BASE_URL % url_path
    response = requests.post(url, data=payload)
    return response.json()

def create_normal_tx(withdrawal_address, input_coin, output_coin,
         return_address=None, destination_tag=None, 
         rs_address=None, api_key=None):
    """withdrawal     = the address for resulting coin to be sent to
    pair       = what coins are being exchanged in the form [input coin]_[output coin]  ie btc_ltc
    returnAddress  = (Optional) address to return deposit to if anything goes wrong with exchange
    destTag    = (Optional) Destination tag that you want appended to a Ripple payment to you
    rsAddress  = (Optional) For new NXT accounts to be funded, you supply this on NXT payment to you
    apiKey     = (Optional) Your affiliate PUBLIC KEY, for volume tracking, affiliate payments, split-shifts, etc...

    example data: {"withdrawal":"AAAAAAAAAAAAA", "pair":"btc_ltc", returnAddress:"BBBBBBBBBBB"}"""
 
    url_path = "shift"     
    payload = {
        'withdrawal': withdrawal_address,
        'pair': "{}_{}".format(input_coin, output_coin),
        'returnAddress': return_address,
        'destTag': destination_tag,
        'rsAddress': rs_address,
        'apiKey': api_key
    }
    payload = {k: v for k,v in payload.items() if v is not None}    
    return _coinswitch_post_request(url_path, payload)

def request_email_receipt(email, tx_id):
    url_path = "mail"
    payload = {
        'email': email,
        'txid': tx_id
    }
    return _coinswitch_post_request(url_path, payload)
  
def create_fixed_amount_tx(amount, withdrawal_address, input_coin, 
        output_coin, return_address=None, destination_tag=None, 
        rs_address=None, api_key=None):
    
    url_path = "sendamount"
    payload = {
        'amount': amount,
        'withdrawal': withdrawal_address,
        'pair': "{}_{}".format(input_coin, output_coin),
        'returnAddress': return_address,
        'destTag': destination_tag,
        'rsAddress': rs_address,
        'apiKey': api_key
    }
    payload = {k: v for k,v in payload.items() if v is not None} 
    return _coinswitch_post_request(url_path, payload)
  
def cancel_tx(address):
    url_path = "cancelpending"
    payload = {
        'address': address,
    }
    return _coinswitch_post_request(url_path, payload)

if __name__ == "__main__":
    print(get_coins())