import requests
import json

BASE_URL = "https://api.coinswitch.co/%s"

headers = {
    'x-api-key': "5CKbkOiu377JSSWnMdFVP7dVNTU7CLbwJTAjlkG4",
    'x-user-ip': "202.88.246.92",
    'content-type': 'application/json'
    }

def _coinswitch_get_request(url_path):
    url = BASE_URL % url_path
    response = requests.request("GET", url, headers=headers)
    raw_list = response.json()
    temp_ss_list = raw_list['data']
    ss_img_dict = {}
    for item in temp_ss_list:
            coin_code = item['symbol'].upper()
            ss_img_dict[coin_code] = {'image':item['logoUrl'],'name':item['name']}  
    return ss_img_dict

def _coinswitch_post_request(url_path, payload):
    url = BASE_URL % url_path
    print(payload)
    print("{\"depositCoin\":\"eth\",\"destinationCoin\":\"ltc\"}")
    # payload = "{\"depositCoin\":\"eth\",\"destinationCoin\":\"ltc\"}"
    response = requests.post(url, data=payload, headers=headers)
    raw_list = response.json()
    temp = raw_list['data']

    json_acceptable_string = payload.replace("'", "\"")
    payload = json.loads(json_acceptable_string)
    temp_dict = {}
    try:
        temp_dict["pair"] = payload['depositCoin']+"_"+payload['destinationCoin']
        temp_dict["rate"]= temp['rate']
        temp_dict["minerFee"]= temp['minerFee']
        temp_dict["limit"]= temp['limitMaxDepositCoin'] 
        temp_dict["minimum"]= temp['limitMinDepositCoin']
        temp_dict["maxLimit"]= temp['limitMaxDepositCoin'] 
    except:
        return temp_dict 
    return temp_dict


def get_coins():
    return _coinswitch_get_request('v2/coins')

def get_rate(input_coin, output_coin):
    url_path = "rate/{}_{}".format(input_coin, output_coin)
    payload = "{\"depositCoin\":\""+input_coin+"\",\"destinationCoin\":\""+output_coin+"\"}"
    return _coinswitch_post_request(url_path, payload)

def get_deposit_limit(input_coin, output_coin):
    url_path = "limit/{}_{}".format(input_coin, output_coin)
    return _coinswitch_get_request(url_path)

def get_market_info(input_coin, output_coin):
    url_path = "v2/rate"
    payload = "{\"depositCoin\":\""+input_coin.lower()+"\",\"destinationCoin\":\""+output_coin.lower()+"\"}"
    return _coinswitch_post_request(url_path, payload)

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
 
    url_path = "v2/order"    
    url = BASE_URL % url_path 


    payload = "{\"depositCoin\":\"%s\",\"destinationCoin\":\"%s\",\"depositCoinAmount\":%s,\"destinationAddress\":{\"address\":\"%s\"},\"refundAddress\":{\"address\":\"%s\"}}" % (input_coin, output_coin, depositCoinAmount, destinationAddress, refundAddress )


    payload = {
        "depositCoin": "btc",
        "destinationCoin": "eth",
        "destinationCoinAmount": 12,
        "destinationAddress": {
            "address": "0xcc1bf6b0625bc23895a47f4991fdb7862e34a563"
        },
        "refundAddress": {
            "address": "1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX"
        }
    }   

    print(headers)
    response = requests.request("POST",url, data=payload, headers=headers)
    raw_list = response.json()
    return raw_list['data']

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
    
    url_path = "v2/order"    
    url = BASE_URL % url_path 

    payload = "{\"depositCoin\":\"%s\",\"destinationCoin\":\"%s\",\"depositCoinAmount\":%s,\"destinationAddress\":{\"address\":\"%s\"},\"refundAddress\":{\"address\":\"%s\"}}" % (input_coin.lower(), output_coin.lower(), amount, withdrawal_address, return_address )

    response = requests.request("POST",url, data=payload, headers=headers)
    raw_list = response.json()
    print(raw_list)
    transaction_details = {'orderId': raw_list['data']['orderId'], 'deposit': raw_list['data']['exchangeAddress']['address'], 'withdrawal':return_address}
    print(transaction_details)
    return transaction_details 
  
def cancel_tx(address):
    url_path = "cancelpending"
    payload = {
        'address': address,
    }
    return _coinswitch_post_request(url_path, payload)

if __name__ == "__main__":
    print(get_coins())