from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from database_connector import db_users, db_settings
from keyboards import Keyboards
from main import dp, bot
from states import ChangeUserInvest
from http_api import Http

kbd = Keyboards()
btn_cancel = kbd.btn_cancel()
main_menu = kbd.main_menu()


@dp.callback_query_handler(text='setup_users')
async def setup_users(message: Message):
    """main kbd to settings for users"""
    mes_id = message['message']['message_id']
    setup_users = kbd.btn_setup_users()
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=f'Here you can setup all account by one click or every account separately.',
        reply_markup=setup_users
    )


@dp.callback_query_handler(Text(startswith="setup_user_info_"))
async def get_users_info(message: Message):
    """returns information about user by btn"""
    data = message.data.split('setup_user_info_')[1]
    mes_id = message['message']['message_id']
    setup_users = kbd.btn_setup_users()
    user_data = db_users.get_users_info(data)
    user_frendly_name = user_data[0]
    user_api_key = user_data[1]
    user_api_secret = user_data[2]
    user_invest = user_data[3]
    user_strategy = user_data[4]
    leverage = user_data[5]
    margin = user_data[6]
    _margin = 'ISOLATED' if margin else 'CROSSED'
    testnet = user_data[7]
    bot_on = user_data[8]
    text = (f'User name: <b>{user_frendly_name}</b>\n'
            f'Api-key: <span class="tg-spoiler">{user_api_key}</span>\n'
            f'Api-secret: <span class="tg-spoiler">{user_api_secret}</span>\n'
            f'Invest: {user_invest}%\n'
            f'Strategy name: {user_strategy}\n'
            f'Leverage: {leverage}x\n'
            f'Margin: {_margin}'
            )
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=text,
        reply_markup=setup_users
    )


@dp.callback_query_handler(Text(startswith="setup_user_change_invest_"))
async def change_users_invest(message: Message, state: FSMContext):
    """get state to change invest procent for user"""
    data = message.data.split('setup_user_change_invest_')[1]
    mes_id = message['message']['message_id']
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=f'In next message enter new invest % for user: {data}.\nInteger 1 to 100.',
    )

    await ChangeUserInvest.invest_part.set()
    await state.update_data(account_name=data)


@dp.callback_query_handler(Text(startswith="btn_change_strategy_"))
async def change_users_invest(message: Message, state: FSMContext):
    """get state to change invest procent for user"""
    data = message.data.split('btn_change_strategy_')[1]
    mes_id = message['message']['message_id']
    strategies_list = db_settings.get_list_of_strategies()
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=f'In next message enter name of strategy which should be added for this user.\n'
             f'Currently you have this strategies: {strategies_list}',
        reply_markup=btn_cancel
    )

    await ChangeUserInvest.strategy_name.set()
    await state.update_data(account_name=data)


@dp.callback_query_handler(Text(startswith="setup_user_delete_user_"))
async def delete_user(message: Message):
    """delete user by btn"""
    data = message.data.split('setup_user_delete_user_')[1]
    mes_id = message['message']['message_id']
    db_users.delete_user(data)
    setup_users = kbd.btn_setup_users()
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=mes_id,
        text=f'User {data} was deleted.',
        reply_markup=setup_users
    )


@dp.message_handler(state=ChangeUserInvest.strategy_name)
async def add_admin(message: Message, state: FSMContext):
    """gets message about new user invest procent"""
    try:
        await state.update_data(strategy_name=message.text)
        data = await state.get_data()
        db_users.change_strategy_for_user(
            data['account_name'], data['strategy_name'])
        setup_users = kbd.btn_setup_users()
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'User {data["account_name"]} strategy was changed to {data["strategy_name"]}.',
            reply_markup=setup_users
        )
    except Exception as err:
        setup_users = kbd.btn_setup_users()
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'Error: {err}.',
            reply_markup=setup_users
        )
    await state.finish()


@dp.message_handler(state=ChangeUserInvest.invest_part)
async def add_admin(message: Message, state: FSMContext):
    """gets message about new user invest procent"""
    try:
        await state.update_data(invest_part=message.text)
        data = await state.get_data()
        db_users.change_invest_for_user(
            data['account_name'], data['invest_part'])
        setup_users = kbd.btn_setup_users()
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'User {data["account_name"]} invest part was changed to {data["invest_part"]}.',
            reply_markup=setup_users
        )
    except Exception as err:
        setup_users = kbd.btn_setup_users()
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f'Error: {err}.',
            reply_markup=setup_users
        )
    await state.finish()


@dp.callback_query_handler(state=ChangeUserInvest.strategy_name, text=['cancel'])
async def cancel_add_new_user(message: Message, state: FSMContext):
    """handles cancel btn"""
    await state.finish()
    await bot.send_message(
        chat_id=message.from_user.id,
        text='Operation canceled.\n\nMenu:',
        reply_markup=main_menu
    )


@dp.callback_query_handler(Text(startswith="setup_user_bot_"))
async def replace_button_bot_on(message: Message):
    """delete user by btn"""
    on_off = message.data.split('setup_user_bot_')[1].split('_')[0]
    user = '_'.join(message.data.split('setup_user_bot_')[1].split('_')[1:])
    mes_id = message['message']['message_id']
    user_data = db_users.get_users_info(user)
    bot_on = user_data[8]
    user_strategy = user_data[4]
    on_off = True if on_off == 'on' else False
    if (on_off and not bot_on) or (not on_off and bot_on):
        if on_off:
            bot_data = db_settings.get_strategy_info(user_strategy)
            if not bot_data:
                await bot.send_message(chat_id=message.from_user.id, text='The strategy for the user is not specified')
                return None
        db_users.change_bot_on_for_user(user, on_off)
        setup_users = kbd.btn_setup_users()
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=mes_id,
            text=f'{user} bot_on changed',
            reply_markup=setup_users
        )
        if on_off:
            user_frendly_name = user_data[0]
            user_api_key = user_data[1]
            user_api_secret = user_data[2]
            user_invest = user_data[3]
            user_strategy = user_data[4]
            leverage = user_data[5]
            margin = bool(user_data[6])
            testnet = bool(user_data[7])
            bot_on = user_data[8]
            name, sma, len_rsi, len_sma, long_entry, long_exit, short_entry, \
            short_exit, timeframe, upd_timeframe, symbols, buy_more_times = bot_data
            user_config = {'user_name': user_frendly_name, 'api_key': user_api_key, 'api_secret': user_api_secret,
                           'invest_part': int(user_invest), 'leverage': int(leverage), 'margin': margin,
                           'testnet': testnet}
            order_data = {'len_rsi': int(len_rsi), 'sma_flag': sma, 'len_sma': int(len_sma),
                          'interval': int(timeframe), 'upd_interval': int(upd_timeframe),
                          'long': {'rsi_ent': int(long_entry), 'rsi_ex': int(long_exit)},
                          'short': {'rsi_ent': int(short_entry), 'rsi_ex': int(short_exit)},
                          'buy_more_times': buy_more_times}
            symbols = str(symbols).split(',')
            await Http().startup_bot(user, symbols, user_config, order_data)
        else:
            await Http().disable_bot(user)


@dp.callback_query_handler(Text(startswith="setup_users_testnet_"))
async def replace_button_bot_on(message: Message):
    """delete user by btn"""
    on_off = message.data.split('setup_users_testnet_')[1].split('_')[0]
    user = '_'.join(message.data.split(
        'setup_users_testnet_')[1].split('_')[1:])
    mes_id = message['message']['message_id']
    user_data = db_users.get_users_info(user)
    testnet = user_data[7]
    on_off = True if on_off == 'on' else False
    if (on_off and not testnet) or (not on_off and testnet):
        db_users.change_testnet_for_user(user, on_off)
        setup_users = kbd.btn_setup_users()
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=mes_id,
            text=f'{user} Testnet changed',
            reply_markup=setup_users
        )
