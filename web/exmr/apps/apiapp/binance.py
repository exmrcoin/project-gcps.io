from binance.client import Client
client = Client('rjMaOqUI6zJlBRe2TxTbbN1ThD0k2Gk3QMRFAJDvZ8wkQCZEqehAw77ymHO9fRjI',
                'gGanHPMl7gHcSwf0qvYZnZXAji56wubc9QVdEuegHPelddMm6AJEdQujdTQylazF')

# get market depth
# depth = client.get_order_book(symbol='BNBBTC')

# place a test market buy order, to place an actual order use the create_order function
# order = client.create_test_order(
#     symbol='BNBBTC',
#     side=Client.SIDE_BUY,
#     type=Client.ORDER_TYPE_MARKET,
#     quantity=100)

# get all symbol prices
# prices = client.get_all_tickers()

# withdraw 100 ETH
# check docs for assumptions around withdrawals
# from binance.exceptions import BinanceAPIException, BinanceWithdrawException
# try:
#     result = client.withdraw(
#         asset='ETH',
#         address='<eth_address>',
#         amount=100)
# except BinanceAPIException as e:
#     print(e)
# except BinanceWithdrawException as e:
#     print(e)
# else:
#     print("Success")

# fetch list of withdrawals
# withdraws = client.get_withdraw_history()

# fetch list of ETH withdrawals
# eth_withdraws = client.get_withdraw_history(asset='ETH')

# get a deposit address for BTC
# address = client.get_deposit_address(asset='BTC')


def getnewaddress(currency):
    try:
        temp = client.get_deposit_address(asset=currency)
        print(temp['address'])
    except:
        temp['address'] = 'an error occured. Please contact support'
    return temp['address']


# start aggregated trade websocket for BNBBTC
def process_message(msg):
    print("message type: {}".format(msg['e']))
    print(msg)
    # do something

# from binance.websockets import BinanceSocketManager
# bm = BinanceSocketManager(client)
# bm.start_aggtrade_socket('BNBBTC', process_message)
# bm.start()

# get historical kline data from any date range

# # fetch 1 minute klines for the last day up until now
# klines = client.get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

# # fetch 30 minute klines for the last month of 2017
# klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")

# # fetch weekly klines since it listed
# klines = client.get_historical_klines("NEOBTC", Client.KLINE_INTERVAL_1WEEK, "1 Jan, 2017")
