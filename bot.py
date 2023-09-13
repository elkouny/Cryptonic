from binance import Client
import imaplib
import email
import math
import time
import datetime

host = 'imap.gmail.com'
username = #Add Gmail Email#
password = #Add Gmail password#

api_key = #Add Binance API Key#
api_secret = #Add Binance API Key Secret#
client = Client(api_key, api_secret)


def round_decimals_down(number: float, decimals: int = 2):
    if decimals == 0:
        return math.floor(number)
    factor = 10 ** decimals
    return math.floor(number * factor) / factor


def round_down(x):
    return float(math.floor(x / 100.0)) * 100


def get_status():
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    mail.select('inbox')

    _, search_data = mail.search(None, 'UNSEEN')
    id_list = search_data[0].split()

    if not id_list:
        print('No unread emails')
        return 'white'

    else:
        alerts = []
        for i in id_list:
            _, data = mail.fetch(i, '(RFC822)')

            for response_part in data:
                if isinstance(response_part, tuple):
                    var_subject = email.message_from_string(response_part[1].decode())['subject']
                    subject_split = var_subject.split(':')
                    if subject_split[0] == "Alert":
                        alerts.append(subject_split[1].lstrip())
    return alerts


valid_value = 0
coin_list = []
a = {}
coin_dictionary = {}
class_check = []
original = round_down(float(client.get_asset_balance(asset="BUSD")["free"]))
diff = round_decimals_down(float(client.get_asset_balance(asset="BUSD")["free"]), 6)
extra_budget = diff - original


def construct(alert_dictionary):
    stat = get_status()
    if stat == 'white':
        return 'white'
    print(stat)

    for n in stat:
        status = (''.join(str(e) for e in n)).split()
        color = status[0]
        ticker = status[1]
        if not coin_list:
            coin_list.append(ticker)
            alert_dictionary = {ticker: color}
        elif coin_list.count(ticker) != 1:
            coin_list.append(ticker)
            alert_dictionary[ticker] = color
        elif coin_list.count(ticker) == 1:
            alert_dictionary.update({ticker: color})
    return alert_dictionary


class Coin:

    def __init__(self, _ticker, _color):
        self.name = _ticker
        self.color = _color
        self.balance = float(client.get_asset_balance(asset=self.name)['free'])
        self.trading_pair = _ticker + 'BUSD'
        self.price = float(client.get_avg_price(symbol=self.trading_pair)['price'])
        self.amount = round_decimals_down(self.balance, 6)
        self.budget = round_down(float(client.get_asset_balance(asset="BUSD")["free"]))
        self.pseudo_budget = round_decimals_down(float(client.get_asset_balance(asset="BUSD")["free"]), 6)
        self.profit_calculator = self.pseudo_budget - extra_budget
        self.coin_quantity = round_decimals_down(float((self.budget / self.price)), 6)
        self.value = round(float(self.price * self.balance), 2)
        self.valid = 0

    def change_color(self, diff_color):
        self.color = diff_color

    def get_att(self):
        return self.name, self.color, self.balance

    def buy(self):
        order = client.order_market_buy(
            symbol=self.trading_pair,
            quantity=self.coin_quantity)

    def sell(self):
        order = client.order_market_sell(
            symbol=self.trading_pair,
            quantity=self.amount)

    def get_profit(self):
        if self.balance_status() == 'open':
            profit = round(((self.value - original) / original) * 100, 2)
            return profit
        elif self.balance_status() == 'close':
            profit = round(((round_decimals_down(self.profit_calculator, 6) - original) / original) * 100, 2)
            return profit

    def stable_coin_status(self):
        if self.pseudo_budget > 100:
            return True
        else:
            return False

    def balance_status(self):
        x = self.price * self.balance

        if x > 5:
            return "open"  # maybe replace open and close with boolean
        return "close"

    def valid_status(self):
        if self.valid == 0 and self.color == 'Red':
            self.valid = 1

        elif self.valid == 1 and self.color == 'Lime' and self.stable_coin_status() is True:
            self.valid = 2

        elif self.valid == 2 and self.color == 'Red' and self.balance_status() == 'open':
            self.valid = 0

    def process(self):
        if self.valid_status() != 2:
            return None

        if self.balance_status() == "open" and self.color == "Lime":
            print(self.name, ": holding position, current value is:", round(self.price, 2))
            pass
        elif self.balance_status() == "open" and self.color == "Red":
            print(self.name, ": closing position, closing value is:", round(self.price, 2))
            self.sell()
            pass
        elif self.balance_status() == "close" and self.color == "Lime":
            print(self.name, ": opening position, current value is:", round(self.price, 2))
            self.buy()
            pass
        elif self.balance_status() == "close" and self.color == "Red":
            print(self.name, "dropping, current value is:", round(self.price, 2))
            pass

    def final(self):
        if self.process() is not None:
            print("$", original, "dollar investment is currently: $", self.value)
            print("Profit is:", self.get_profit(), "%")
            print(self.valid)
        else:
            pass


while True:
    print(datetime.datetime.now())
    loop_time = time.time()
    a = construct(a)

    if a == 'white':
        print("Alert not received no changes have occurred.")

    else:
        if len(coin_dictionary) == 0:
            for i in a:
                coin_dictionary[i] = Coin(i, a[i])

        else:
            for i in coin_list:
                if i in coin_dictionary:
                    coin_dictionary[i].change_color(a[i])
                else:
                    coin_dictionary[i] = Coin(i, a[i])

        for i in coin_list:
            print('Program ran through', i)
            coin_dictionary[i].final()

    print("Loop time elapsed: {:.2f}s".format(time.time() - loop_time))
    time.sleep(60)
    # exit()
