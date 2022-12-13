from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterNewUser(StatesGroup):
    """State for register new user."""
    friendly_name = State()
    api_key = State()
    api_secret = State()
    invest_percent = State()
    Leverage = State()
    Margin = State()


class RegisterNewAdmin(StatesGroup):
    """State for register new admin."""
    admin_id = State()


class DeleteAdmin(StatesGroup):
    """State for delete admin."""
    admin_id = State()


class ChangeUserInvest(StatesGroup):
    """State change invest part for user."""
    account_name = State()
    invest_part = State()
    strategy_name = State()

  
class StrategyConfig(StatesGroup):
    """State for config new strategy."""
    name = State()
    len_rsi = State()
    len_sma = State()
    long_entry = State()
    long_exit = State()
    short_entry = State()
    short_exit = State()
    timeframe = State()
    upd_timeframe = State()
    rsi_sma = State()
    symbols = State()
    buy_more_times = State()
