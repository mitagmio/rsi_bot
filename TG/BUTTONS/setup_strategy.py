from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from database_connector import db_settings
from keyboards import Keyboards
from main import dp, bot

kbd = Keyboards()
btn_cancel = kbd.btn_cancel()


@dp.callback_query_handler(text='setup_strategy')
async def setup_users(message: Message):
    """main kbd to settings for users"""
    mes_id = message['message']['message_id']
    setup_strategies = kbd.btn_setup_strategies()
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=f'Here you can setup all strategies by one click or every account separately.',
        reply_markup=setup_strategies
    )


@dp.callback_query_handler(Text(startswith="setup_strategy_info_"))
async def get_users_info(message: Message):
    """returns information about user by btn"""
    data = message.data.split('setup_strategy_info_')[1]
    mes_id = message['message']['message_id']
    setup_strategies = kbd.btn_setup_strategies()
    strategy_data = db_settings.get_strategy_info(data)
    strategy_friendly_name = strategy_data[0]
    if strategy_data[1]:
        strategy_rsi_sma = 'SMA'
    else:
        strategy_rsi_sma = 'RSI'
    strategy_len_rsi = strategy_data[2]
    strategy_len_sma = strategy_data[3]
    strategy_long_entry = strategy_data[4]
    strategy_long_exit = strategy_data[5]
    strategy_short_entry = strategy_data[6]
    strategy_short_exit = strategy_data[7]
    strategy_timeframe = strategy_data[8]
    strategy_upd_timeframe = strategy_data[9]
    text = (f'Strategy: <b>{strategy_friendly_name}</b>\n'
            f'RSI or SMA(from RSI) setup for entry or exit: {strategy_rsi_sma}\n'
            f'Length of RSI: {strategy_len_rsi}\n'
            f'Length of SMA: {strategy_len_sma}\n'
            f'Long entry condition: {strategy_long_entry}\n'
            f'Long exit condition: {strategy_long_exit}\n'
            f'Short entry condition: {strategy_short_entry}\n'
            f'Short exit condition: {strategy_short_exit}\n'
            f'Timeframe of RSI and SMA: {strategy_timeframe} min\n'
            f'Update frequency: {strategy_upd_timeframe} sec\n'
            )

    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=text,
        reply_markup=setup_strategies
    )


@dp.callback_query_handler(Text(startswith="setup_strategy_delete_"))
async def delete_user(message: Message):
    """delete user by btn"""
    data = message.data.split('setup_strategy_delete_')[1]
    mes_id = message['message']['message_id']
    db_settings.delete_strategy(data)
    setup_strategies = kbd.btn_setup_strategies()
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=f'User {data} was deleted.',
        reply_markup=setup_strategies
    )

@dp.callback_query_handler(Text(startswith="setup_strategy_symbols_"))
async def get_symbols(message: Message):
    """get symbols from the db"""
    data = message.data.split('setup_strategy_symbols_')[1]
    mes_id = message['message']['message_id']
    setup_strategies = kbd.btn_setup_strategies()
    symbols = db_settings.get_symbols(data)
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=f'Strategy symbols: {symbols}',
        reply_markup=setup_strategies
    )
