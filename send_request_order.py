from typing import Callable

import numpy as np
import pandas as pd
import requests
from pybit.usdt_perpetual import HTTP
from loguru_settings import log


def switch_mode(user_data: dict, order_data: dict):
    bybit = HTTP(
        api_key=user_data['api_key'],
        api_secret=user_data['api_secret'],
        endpoint='https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com')
    try:
        bybit.position_mode_switch(symbol=order_data['symbol'], mode='BothSide')
    except Exception as e:
        if 'mode not modified' in str(e):
            pass
        else:
            raise Exception(e)


def set_leverage_margin(user_data: dict, order_data: dict):
    '''The func tries to set leverage and returns given leverage.
    In exception case it just returns given leverage'''
    bybit = HTTP(
        api_key=user_data['api_key'],
        api_secret=user_data['api_secret'],
        endpoint='https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
    )
    try:
        bybit.cross_isolated_margin_switch(
            symbol=order_data['symbol'],
            buy_leverage=user_data['leverage'],
            sell_leverage=user_data['leverage'],
            is_isolated=user_data['margin']
        )
    except Exception as e:
        if 'Isolated not modified' in str(e):
            set_leverage(user_data, order_data)
        else:
            raise Exception(e)


def set_leverage(user_data: dict, order_data: dict):
    '''The func tries to set leverage and returns given leverage.
    In exception case it just returns given leverage'''
    bybit = HTTP(
        api_key=user_data['api_key'],
        api_secret=user_data['api_secret'],
        endpoint='https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com')
    try:
        bybit.set_leverage(
            symbol=order_data['symbol'],
            buy_leverage=user_data['leverage'],
            sell_leverage=user_data['leverage']
        )
    except:
        pass


def get_tick_scale_price_and_qty(user_data: dict, order_data: dict):
    '''The func returns tick_size, scale_price and scale_qty'''
    try:
        url = 'https://api2-testnet.bybit.com/contract/v5/product/dynamic-symbol-list?filter=all&token=GMmJus7A'
        resp = requests.get(url).json()
        for i in resp['result']['LinearPerpetual']:
            if i['symbolName'] == order_data['symbol']:
                price_scale = i['priceFraction']
                try:
                    s = str(i['minQty'])
                    qty_scale = len(s[s.index('.') + 1:])
                except:
                    qty_scale = 0
                tick_size = float(i['tickSize'])

                return tick_size, price_scale, qty_scale
    except Exception as e:
        price_scale = None
        tick_size = None
        endpoint = 'https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
        url = endpoint + '/v2/public/symbols'
        symbols = requests.get(url).json()['result']
        for i in symbols:
            if i['name'] == order_data['symbol']:
                tick_size = i['price_filter']['tick_size']
                price_scale = i['scale_price']

        if price_scale is None:
            raise Exception(f'There is no scale price for {order_data["symbol"]}')

        endpoint = 'https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
        url = endpoint + f'/v2/public/orderBook/L2?symbol={order_data["symbol"]}'
        bids_asks = requests.get(url).json()['result']
        temp_scale = 0
        for i in bids_asks:
            s = i['size']
            if temp_scale < len(s[s.index('.') + 1:]):
                temp_scale = len(s[s.index('.') + 1:])
        else:
            qry_scale = temp_scale
        return tick_size, price_scale, qry_scale


def calc_rsi(over: pd.Series, fn_roll: Callable) -> pd.Series:
    '''A free form for calculating rsi'''
    delta = over.diff()
    delta = delta[1:]

    up, down = delta.clip(lower=0), delta.clip(upper=0).abs()

    roll_up, roll_down = fn_roll(up), fn_roll(down)
    rs = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi[:] = np.select([roll_down == 0, roll_up == 0, True], [100, 0, rsi])
    rsi.name = 'rsi'

    return rsi


def calc_sma(data_rsi, len_sma):
    '''[oldest,..., newest]'''
    list_sma = []
    for i in range(len_sma, len(data_rsi) + 1):
        try:
            sma = sum(data_rsi[i - len_sma:i]) / len_sma
        except:
            sma = 0
        list_sma.append(sma)
    return list_sma


def rsi_sma(order_data: dict, data: dict):
    closes = data['close']
    stockCloses = pd.DataFrame({'stockValues': list(reversed(closes))})
    try:
        rsi_rma = calc_rsi(stockCloses['stockValues'],
                           lambda s: s.ewm(alpha=1 / order_data['len_rsi']).mean()).tolist()
    except:
        rsi_rma = []
    sma = list(reversed(calc_sma(rsi_rma, order_data['len_sma'])))
    rsi_rma = list(reversed(rsi_rma))

    if len(rsi_rma) < len(closes):
        rsi_rma += [None for _ in range(len(closes) - len(rsi_rma))]

    if len(sma) < len(closes):
        sma += [None for _ in range(len(closes) - len(sma))]

    data['rsi'] = rsi_rma
    data['sma'] = sma
    return data


def get_available_balance(user_data: dict, order_data: dict):
    '''The func gets and returns available balance'''
    bybit = HTTP(
        api_key=user_data['api_key'],
        api_secret=user_data['api_secret'],
        endpoint='https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
    )
    balance = bybit.get_wallet_balance(coin="USDT")['result']['USDT']['available_balance']
    return balance


def get_last_price(user_data: dict, order_data: dict):
    '''The func returns last price of current symbol'''
    endpoint = 'https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
    url = endpoint + f'/v2/public/tickers?symbol={order_data["symbol"]}'
    data = requests.get(url).json()['result']
    return float(data[0]['mark_price'])


def create_entry_order(user_data: dict, order_data: dict):
    '''The func enters a position'''

    invest_part_dol = round(get_available_balance(user_data, order_data) * user_data['invest_part'] / 100, 1)
    last_price = get_last_price(user_data, order_data)
    qty = round(invest_part_dol * user_data['leverage'] / last_price, order_data['scale_qty'])

    bybit = HTTP(
        api_key=user_data['api_key'],
        api_secret=user_data['api_secret'],
        endpoint='https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
    )
    req = bybit.place_active_order(
        symbol=order_data['symbol'],
        side=order_data['side'],
        order_type="Market",
        reduce_only=False,
        qty=qty,
        close_on_trigger=False,
        time_in_force="GoodTillCancel"
    )
    log.info(req)
    return req


def create_exit_order(user_data: dict, order_data: dict):
    '''The func enters a position'''
    qty = get_position_qty(user_data, order_data)
    bybit = HTTP(
        api_key=user_data['api_key'],
        api_secret=user_data['api_secret'],
        endpoint='https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
    )

    req = bybit.place_active_order(
        symbol=order_data['symbol'],
        side=order_data['side'],
        order_type="Market",
        reduce_only=True,
        qty=qty,
        close_on_trigger=False,
        time_in_force="GoodTillCancel"
    )
    log.info(req)
    return req


def get_position_qty(user_data: dict, order_data: dict):
    bybit = HTTP(
        api_key=user_data['api_key'],
        api_secret=user_data['api_secret'],
        endpoint='https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
    )
    position = bybit.my_position(symbol=order_data['symbol'])['result']
    qty = tuple(i['size'] for i in position if i['size'])
    return qty[0]


def get_position(user_data: dict, order_data: dict):
    bybit = HTTP(
        api_key=user_data['api_key'],
        api_secret=user_data['api_secret'],
        endpoint='https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
    )

    position = bybit.my_position(symbol=order_data['symbol'])['result']
    # print(position)
    return position


def close_all_position(user_data: dict, order_data: dict):
    '''The func just closes all positions'''
    bybit = HTTP(
        api_key=user_data['api_key'],
        api_secret=user_data['api_secret'],
        endpoint='https://api-testnet.bybit.com' if user_data['testnet'] else 'https://api.bybit.com'
    )
    positions = bybit.my_position()['result']
    positions = tuple(filter(lambda x: x['data']['size'], positions))
    while positions:
        for i in positions:
            side = 'Sell' if i['data']['side'] == 'Buy' else 'Buy'
            bybit.place_active_order(
                symbol=i['data']['symbol'],
                side=side,
                order_type="Market",
                reduce_only=True,
                qty=i['data']['size'],
                close_on_trigger=True,
                time_in_force="GoodTillCancel",
                position_idx=i['data']['position_idx']
            )
        else:
            positions = bybit.my_position()['result']
            positions = tuple(filter(lambda x: x['data']['size'], positions))
