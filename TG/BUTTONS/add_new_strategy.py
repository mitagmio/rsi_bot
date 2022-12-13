from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram import Bot
from keyboards import Keyboards
from main import dp, bot
from database_connector import db_settings
from states import StrategyConfig
import re
import aiohttp

kbd = Keyboards()
btn_cancel = kbd.btn_cancel()
main_menu = kbd.main_menu()

bot: Bot


@dp.callback_query_handler(text='new_strategy')
async def config_strategy(message: Message):
    """Handles btn 'config strategy' click."""
    mes_id = message['message']['message_id']
    config_strategy_kbd = kbd.btn_config_strategy()
    text = 'Now you dont have strategy, press btn to setup it.'
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=text,
        reply_markup=config_strategy_kbd
    )


@dp.callback_query_handler(Text(startswith="config_setup_"))
async def register_new_user(message: Message):
    """handles singly btn click"""
    mes_id = message['message']['message_id']
    manual_text = ("""11 steps: 
    1 - Name of strategy
    2 - Length of RSI (from 0 to 100)
    3 - Length of SMA (from 0 to 100)
    4 - Long entry condition (from 0 to 100)
    5 - Long exit condition (from 0 to 100)
    6 - Short entry condition (from 0 to 100)
    7 - Short exit condition (from 0 to 100)
    8 - Timeframe of RSI and SMA (from 1 min to 1440 min)
    9 - Update frequency (0 is same as Timeframe (it means on close candle) else from 1 sec to 60 sec)
    10 - RSI or SMA(from RSI) setup for entry or exit
    11 - Crypto-pairs
    12 - buy_more_times
    Now send me name of strategy:""")
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=manual_text,
        reply_markup=btn_cancel
    )
    await StrategyConfig.name.set()


@dp.message_handler(state=StrategyConfig.name)
async def get_strategy_takes(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await bot.send_message(
        chat_id=message.from_user.id,
        text='Write Length of RSI (from 0 to 100)'
    )
    data = await state.get_data()
    await StrategyConfig.next()


@dp.message_handler(state=StrategyConfig.len_rsi)
async def get_strategy_takes(message: Message, state: FSMContext):
    if re.search(r'(^\d+$)', message.text):
        if 0 <= int(message.text) <= 100:
            await state.update_data(len_rsi=message.text)
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Write Length of SMA (from 0 to 100)'
            )
            data = await state.get_data()
            await StrategyConfig.next()
        else:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="You wrote wrong number."
            )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You didn't enter a number."
        )


@dp.message_handler(state=StrategyConfig.len_sma)
async def get_strategy_takes(message: Message, state: FSMContext):
    if re.search(r'(^\d+$)', message.text):
        if 0 <= int(message.text) <= 100:
            await state.update_data(len_sma=message.text)
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Write Long entry condition (from 0 to 100)'
            )
            data = await state.get_data()
            await StrategyConfig.next()
        else:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="You wrote wrong number."
            )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You didn't enter a number."
        )


@dp.message_handler(state=StrategyConfig.long_entry)
async def get_strategy_takes(message: Message, state: FSMContext):
    if re.search(r'(^\d+$)', message.text):
        if 0 <= int(message.text) <= 100:
            await state.update_data(long_entry=message.text)
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Write Long exit condition (from 0 to 100)'
            )
            data = await state.get_data()
            await StrategyConfig.next()
        else:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="You wrote wrong number."
            )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You didn't enter a number."
        )


@dp.message_handler(state=StrategyConfig.long_exit)
async def get_strategy_takes(message: Message, state: FSMContext):
    if re.search(r'(^\d+$)', message.text):
        if 0 <= int(message.text) <= 100:
            await state.update_data(long_exit=message.text)
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Write Short entry condition (from 0 to 100)'
            )
            data = await state.get_data()
            await StrategyConfig.next()
        else:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="You wrote wrong number."
            )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You didn't enter a number."
        )


@dp.message_handler(state=StrategyConfig.short_entry)
async def get_strategy_takes(message: Message, state: FSMContext):
    if re.search(r'(^\d+$)', message.text):
        if 0 <= int(message.text) <= 100:
            await state.update_data(short_entry=message.text)
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Write Short exit condition (from 0 to 100)'
            )
            data = await state.get_data()
            await StrategyConfig.next()
        else:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="You wrote wrong number."
            )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You didn't enter a number."
        )


@dp.message_handler(state=StrategyConfig.short_exit)
async def get_strategy_takes(message: Message, state: FSMContext):
    if re.search(r'(^\d+$)', message.text):
        if 0 <= int(message.text) <= 100:
            await state.update_data(short_exit=message.text)
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Write Timeframe of RSI and SMA (from 1 min to 1440 min)'
            )
            data = await state.get_data()
            await StrategyConfig.next()
        else:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="You wrote wrong number."
            )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You didn't enter a number."
        )


@dp.message_handler(state=StrategyConfig.timeframe)
async def get_strategy_takes(message: Message, state: FSMContext):
    if re.search(r'(^\d+$)', message.text):
        if 1 <= int(message.text) <= 1440:
            await state.update_data(timeframe=message.text)
            await bot.send_message(
                chat_id=message.from_user.id,
                text='Write update frequency (0 is same as Timeframe (it means on close candle) else from 1 sec to 60 sec)'
            )
            data = await state.get_data()
            await StrategyConfig.next()
        else:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="You wrote wrong number."
            )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You didn't enter a number."
        )


@dp.message_handler(state=StrategyConfig.upd_timeframe)
async def get_strategy_takes(message: Message, state: FSMContext):
    if re.search(r'(^\d+$)', message.text):
        if 0 <= int(message.text) <= 60:
            await state.update_data(upd_timeframe=message.text)
            await bot.send_message(
                chat_id=message.from_user.id,
                text='<code>RSI</code> or <code>SMA</code>(from RSI) setup for entry or exit'
            )
            data = await state.get_data()
            await StrategyConfig.next()
        else:
            await bot.send_message(
                chat_id=message.from_user.id,
                text="You wrote wrong number."
            )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You didn't enter a number."
        )


@dp.message_handler(state=StrategyConfig.rsi_sma)
async def get_strategy_takes(message: Message, state: FSMContext):
    if message.text == 'SMA':
        await state.update_data(rsi_sma=True)
    elif message.text == 'RSI':
        await state.update_data(rsi_sma=False)
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text='You can only enter RSI or SMA'
        )
    if message.text in ['SMA', 'RSI']:
        data = await state.get_data()
        msg = await bot.send_message(chat_id=message.chat.id, text='Getting data from the exchange...')
        txt = '<code>'
        resp = 'error'
        for _ in range(5):
            try:
                async with aiohttp.request(
                        method='GET',
                        url='https://api2.bybit.com/contract/v5/product/dynamic-symbol-list',
                        params={'filter': 'all'}
                )as response:
                    resp = await response.json()
                    resp = resp['result']['LinearPerpetual']
                break
            except:
                continue
        if resp == 'error':
            await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text='Bybit error')
            return ''
        for i in resp:
            txt += i['symbolName'] + ','
        txt = txt[:-1]
        txt += '</code>'
        await bot.edit_message_text(
            chat_id=message.from_user.id, message_id=msg.message_id,
            text=txt
        )
        await StrategyConfig.next()


@dp.message_handler(state=StrategyConfig.symbols)
async def get_strategy_takes(message: Message, state: FSMContext):
    check_msg = re.findall('([A-Z]{6,12},){1,500}', message.text)
    if check_msg:
        await bot.send_message(message.chat.id, 'Enter a number for buy more times - from 1 to 100')
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You didn't enter a Crypto-pairs."
        )
        return ''
    await state.update_data(symbols=message.text)
    await StrategyConfig.next()


@dp.message_handler(state=StrategyConfig.buy_more_times)
async def get_strategy_takes(msg: Message, state: FSMContext):
    num = msg.text
    user_id = msg.chat.id
    if not num.isdigit():
        await bot.send_message(chat_id=user_id, text='Invalid format')
        return ''
    elif int(num) < 1 or int(num) > 100:
        await bot.send_message(chat_id=user_id, text='Invalid format')
        return ''
    await state.update_data(buy_more_times=int(msg.text))
    data = await state.get_data()
    await state.finish()
    db_settings.update_table(data)
    menu_markup = kbd.main_menu()
    await msg.answer(
        text='Hello, you are in test bot.',
        reply_markup=menu_markup
    )


@dp.callback_query_handler(state=[
    StrategyConfig.name,
    StrategyConfig.len_rsi,
    StrategyConfig.len_sma,
    StrategyConfig.long_entry,
    StrategyConfig.long_exit,
    StrategyConfig.short_entry,
    StrategyConfig.short_exit,
    StrategyConfig.timeframe,
    StrategyConfig.upd_timeframe,
    StrategyConfig.rsi_sma,
    StrategyConfig.symbols,
    StrategyConfig.buy_more_times],
    text=['cancel'])
async def cancel_add_new_user(message: Message, state: FSMContext):
    """handles cancel btn"""
    await state.finish()
    await bot.send_message(
        chat_id=message.from_user.id,
        text='Operation canceled.\n\nMenu:',
        reply_markup=main_menu
    )
