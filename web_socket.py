import time

import requests
from pybit import usdt_perpetual
from TG.config import BOT_TOKEN, channel_id
import send_request_order
from loguru_settings import log


def write_log(user_name, symbol, msg, data_0, data_1, req):
    txt = f"{user_name} {symbol} {msg} {round(data_0, 2)} {round(data_1, 2)}"
    log.info(txt)
    requests.post(url='https://api.telegram.org/bot{0}/{1}'.format(BOT_TOKEN, 'sendMessage'),
                  data={'chat_id': channel_id, 'text': txt})
    if req['ret_msg'] == 'OK':
        message = f"✅ {user_name} {symbol} {msg}"
    else:
        message = f"❌ {user_name} {symbol} {msg}"

    requests.post(url='https://api.telegram.org/bot{0}/{1}'.format(BOT_TOKEN, 'sendMessage'),
                  data={'chat_id': channel_id, 'text': message})


class Socket:
    def __init__(self, user_data, order_data):
        self.user_data = user_data
        self.order_data = order_data
        log.info(self.order_data)

        send_request_order.switch_mode(self.user_data, self.order_data)
        send_request_order.set_leverage_margin(self.user_data, self.order_data)
        self.order_data['tick_size'], self.order_data['price_scale'], self.order_data['scale_qty'] = \
            send_request_order.get_tick_scale_price_and_qty(self.user_data, self.order_data)

        self.ws = None
        self.last_candle = None
        self.last_upd = None

        self.counter_buys = 0

        self.order_data['side'] = ''
        self.order_data['link_id'] = ''
        self.in_position = False

        self.candles_data = {}
        self.get_start_data()

    def start(self):
        try:
            self.ws = self._connect()
            self._subscribe()
        except Exception as e:
            log.info(e)
            exit()

        if self.order_data['upd_interval'] < 0:
            upd = self.order_data['upd_interval'] * -1
        elif self.order_data['upd_interval'] == 0:
            upd = 60
        else:
            upd = self.order_data['upd_interval']
        while True:
            time.sleep(upd)
            if not self.ws.is_connected():
                exit()

    def get_start_data(self):
        candles_data_names = ['close', 'time']
        for i in candles_data_names:
            self.candles_data[i] = []
            [self.candles_data[i].append(None) for _ in range(200)]

        from_time = int(time.time()) - 60 * self.order_data['interval'] * 200
        endpoint = 'https://api-testnet.bybit.com' if self.user_data['testnet'] else 'https://api.bybit.com'

        url = f'{endpoint}/public/linear/kline?symbol={self.order_data["symbol"]}' \
              f'&interval={self.order_data["interval"]}&limit=200&from={from_time}'

        candles = requests.get(url).json()['result']
        if candles:
            for i in candles:
                self.candles_data['close'].insert(0, float(i['close']))
                self.candles_data['close'].pop(-1)
                self.candles_data['time'].insert(0, int(i['open_time']) + 60 * self.order_data['interval'])
                self.candles_data['time'].pop(-1)

    def _connect(self):
        return usdt_perpetual.WebSocket(
            test=True if self.user_data['testnet'] else False,
            ping_interval=30,  # the default is 30
            ping_timeout=10,  # the default is 10
            domain="bybit"  # the default is "bybit"
        )

    def _subscribe(self):
        self.ws.kline_stream(self.handle_message, self.order_data['symbol'], self.order_data['interval'])

    def handle_message(self, msg):
        if self.order_data['upd_interval'] == -1:
            self.candles_data['time'].insert(0, int(msg['timestamp_e6'] / (1000 * 1000)))
            self.update_candles_data(msg)
            self.do()

        elif self.order_data['upd_interval'] == 0:
            if int(msg['data'][0]['end']) != self.candles_data['time'][0]:
                self.candles_data['time'].insert(0, int(msg['data'][0]['end']))
                self.update_candles_data(msg)
                self.do()

        else:
            if int(msg['timestamp_e6'] / (1000 * 1000)) >= \
                    self.candles_data['time'][0] + self.order_data['upd_interval']:
                self.candles_data['time'].insert(0, int(msg['timestamp_e6'] / (1000 * 1000)))
                self.update_candles_data(msg)
                self.do()

    def update_candles_data(self, msg):
        self.candles_data['close'].insert(0, float(msg['data'][0]['close']))
        self.candles_data['close'].pop(-1)
        self.candles_data['time'].pop(-1)

    def do(self):
        self.candles_data = send_request_order.rsi_sma(self.order_data, self.candles_data)
        log.info(f'{self.order_data["symbol"]} '
                 f'rsi: {round(self.candles_data["rsi"][1], 2)} - {round(self.candles_data["rsi"][0], 2)} '
                 f'sma: {round(self.candles_data["sma"][1], 2)} - {round(self.candles_data["sma"][0], 2)}')

        if self.order_data['sma_flag']:
            if self.counter_buys < self.order_data['buy_more_times']:
                if self.candles_data['sma'][1] < self.order_data['long']['rsi_ent'] < self.candles_data['sma'][0]:
                    self.order_data['side'] = 'Buy'
                    req = send_request_order.create_entry_order(self.user_data, self.order_data)
                    write_log(self.user_data['user_name'], self.order_data['symbol'], 'entry long sma',
                              self.candles_data['sma'][1], self.candles_data['sma'][0], req)
                    self.counter_buys += 1

                elif self.candles_data['sma'][1] > self.order_data['short']['rsi_ent'] > self.candles_data['sma'][0]:
                    self.order_data['side'] = 'Sell'
                    req = send_request_order.create_entry_order(self.user_data, self.order_data)
                    write_log(self.user_data['user_name'], self.order_data['symbol'], 'entry short sma',
                              self.candles_data['sma'][1], self.candles_data['sma'][0], req)
                    self.counter_buys += 1

            if self.order_data['side'] == 'Buy':
                if self.candles_data['sma'][1] < self.order_data['long']['rsi_ex'] < self.candles_data['sma'][0]:
                    self.order_data['side'] = 'Sell'
                    req = send_request_order.create_exit_order(self.user_data, self.order_data)
                    write_log(self.user_data['user_name'], self.order_data['symbol'], 'exit long sma',
                              self.candles_data['sma'][1], self.candles_data['sma'][0], req)
                    self.order_data['side'] = ''
                    self.counter_buys = 0

            elif self.order_data['side'] == 'Sell':
                if self.candles_data['sma'][1] > self.order_data['short']['rsi_ex'] > self.candles_data['sma'][0]:
                    self.order_data['side'] = 'Buy'
                    req = send_request_order.create_exit_order(self.user_data, self.order_data)
                    write_log(self.user_data['user_name'], self.order_data['symbol'], 'exit short sma',
                              self.candles_data['sma'][1], self.candles_data['sma'][0], req)
                    self.order_data['side'] = ''
                    self.counter_buys = 0

        else:
            if self.counter_buys < self.order_data['buy_more_times']:
                if self.candles_data['rsi'][1] < self.order_data['long']['rsi_ent'] < self.candles_data['rsi'][0]:
                    self.order_data['side'] = 'Buy'
                    req = send_request_order.create_entry_order(self.user_data, self.order_data)
                    write_log(self.user_data['user_name'], self.order_data['symbol'], 'entry long rsi',
                              self.candles_data['rsi'][1], self.candles_data['rsi'][0], req)
                    self.counter_buys += 1

                elif self.candles_data['rsi'][1] > self.order_data['short']['rsi_ent'] > self.candles_data['rsi'][0]:
                    self.order_data['side'] = 'Sell'
                    req = send_request_order.create_entry_order(self.user_data, self.order_data)
                    write_log(self.user_data['user_name'], self.order_data['symbol'], 'entry short rsi',
                              self.candles_data['rsi'][1], self.candles_data['rsi'][0], req)
                    self.counter_buys += 1

            if self.order_data['side'] == 'Buy':
                if self.candles_data['rsi'][1] < self.order_data['long']['rsi_ex'] < self.candles_data['rsi'][0]:
                    self.order_data['side'] = 'Sell'
                    req = send_request_order.create_exit_order(self.user_data, self.order_data)
                    write_log(self.user_data['user_name'], self.order_data['symbol'], 'exit long rsi',
                              self.candles_data['rsi'][1], self.candles_data['rsi'][0], req)
                    self.order_data['side'] = ''
                    self.counter_buys = 0

            elif self.order_data['side'] == 'Sell':
                if self.candles_data['rsi'][1] > self.order_data['short']['rsi_ex'] > self.candles_data['rsi'][0]:
                    self.order_data['side'] = 'Buy'
                    req = send_request_order.create_exit_order(self.user_data, self.order_data)
                    write_log(self.user_data['user_name'], self.order_data['symbol'], 'exit short rsi',
                              self.candles_data['rsi'][1], self.candles_data['rsi'][0], req)
                    self.order_data['side'] = ''
                    self.counter_buys = 0
