from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database_connector import db_users
from database_connector import db_settings


class Keyboards:

    def __init__(self):
        self.btn_back_to_menu = InlineKeyboardButton(
            text='↩️Back to menu',
            callback_data='back_to_menu'
        )

    def single_menu_btn(self):
        """Keyboard back to menu btn."""
        menu_btn = InlineKeyboardMarkup(row_width=2)
        menu_btn.insert(self.btn_back_to_menu)

        return menu_btn

    def main_menu(self):
        """returns start markup"""
        main_menu = InlineKeyboardMarkup(row_width=2)

        btn_add_new_user = InlineKeyboardButton(
            text='Add new user',
            callback_data='new_user'
        )
        btn_setup_users = InlineKeyboardButton(
            text='Setup users',
            callback_data='setup_users'
        )
        btn_add_new_strategy = InlineKeyboardButton(
            text='Add new strategy',
            callback_data='new_strategy'
        )
        btn_setup_strategy = InlineKeyboardButton(
            text='Setup strategy',
            callback_data='setup_strategy'
        )
        # btn_setup_bots = InlineKeyboardButton(
        #     text='Setup bot',
        #     callback_data='setup_bot'
        # )
        btn_add_admin = InlineKeyboardButton(
            text='Admin manage',
            callback_data='add_admin'
        )

        btn_list = [btn_add_new_user, btn_setup_users, btn_add_new_strategy,
                    btn_setup_strategy, #btn_setup_bots,
                     btn_add_admin]

        for btn in btn_list:
            main_menu.insert(btn)

        return main_menu

    def btn_to_setup_bot(self, bot_status, user) ->InlineKeyboardButton:
        """Keyboard on or off bot."""

        btn_on = InlineKeyboardButton(
            text='✅Bot turn ON',
            callback_data=f'setup_user_bot_off_{user}'
        )

        btn_off = InlineKeyboardButton(
            text='⛔️Bot turn OFF',
            callback_data=f'setup_user_bot_on_{user}'
        )

        if bot_status:
            return btn_on
        else:
            return btn_off

    def btn_to_testnet(self, testnet, user) ->InlineKeyboardButton:
        """Keyboard on or off bot."""

        mainnet_btn = InlineKeyboardButton(
            text='✅Mainnet',
            callback_data=f'setup_users_testnet_on_{user}'
        )

        testnet_btn = InlineKeyboardButton(
            text='✅Testnet',
            callback_data=f'setup_users_testnet_off_{user}'
        )

        if not testnet:
            return mainnet_btn
        else:
            return testnet_btn


    def btn_setup_users(self,):
        """Keyboard settings for user."""
        users_list = db_users.get_list_of_users()
        btn_to_setup_bot = InlineKeyboardMarkup()
        for user in users_list:
            btn_info = InlineKeyboardButton(
                text=f'ℹ️{user}',
                callback_data=f'setup_user_info_{user}'
            )
            btn_change_invest = InlineKeyboardButton(
                text=f'⚙️invest',
                callback_data=f'setup_user_change_invest_{user}'
            )
            btn_change_strategy = InlineKeyboardButton(
                text=f'⚙️strategy',
                callback_data=f'btn_change_strategy_{user}'
            )
            btn_delete = InlineKeyboardButton(
                text=f'❌delete ',
                callback_data=f'setup_user_delete_user_{user}'
            )
            btn_to_setup_bot.row(btn_info,btn_change_invest,btn_change_strategy,btn_delete)
            user_data = db_users.get_users_info(user)
            testnet = user_data[7]
            bot_on = user_data[8]
            bot_on_button = self.btn_to_setup_bot(bot_on,user)
            testnet_button = self.btn_to_testnet(testnet,user)
            btn_to_setup_bot.row(bot_on_button, testnet_button)
        btn_to_setup_bot.row(self.btn_back_to_menu)
        return btn_to_setup_bot

    def btn_setup_strategies(self):
        """Keyboard settings for user."""
        strategies_list = db_settings.get_list_of_strategies()
        btn_to_setup_bot = InlineKeyboardMarkup(row_width=3)
        for strategy in strategies_list:
            btn_info = InlineKeyboardButton(
                text=f'ℹ️{strategy}',
                callback_data=f'setup_strategy_info_{strategy}'
            )
            btn_symbols = InlineKeyboardButton(text='Get symbols', callback_data=f'setup_strategy_symbols_{strategy}')
            btn_delete = InlineKeyboardButton(
                text=f'❌delete ',
                callback_data=f'setup_strategy_delete_{strategy}'
            )
            btn_to_setup_bot.insert(btn_info)
            btn_to_setup_bot.insert(btn_symbols)
            btn_to_setup_bot.insert(btn_delete)
        btn_to_setup_bot.insert(self.btn_back_to_menu)
        return btn_to_setup_bot

    def btn_config_strategy(self):
        """Keyboard to config strategy."""
        btn_config_strategy = InlineKeyboardMarkup(row_width=1)

        btn_nubmer_of_takes = InlineKeyboardButton(
            text='Setup strategy',
            callback_data='config_setup_strategy'
        )

        btn_config_strategy.insert(btn_nubmer_of_takes)
        btn_config_strategy.insert(self.btn_back_to_menu)

        return btn_config_strategy

    def btn_cancel(self):
        """Keyboard to cancel current move.."""
        kbd_cancel = InlineKeyboardMarkup(row_width=1)
        btn_cancel = InlineKeyboardButton(
            text='✖ Cancel',
            callback_data='cancel'
        )

        kbd_cancel.insert(btn_cancel)

        return kbd_cancel

    def admin_settings(self):
        """Keyboard to settings for admins."""
        kbd_admin = InlineKeyboardMarkup(row_width=1)

        btn_add_admin = InlineKeyboardButton(
            text='Add admin',
            callback_data='admin_settings_add'
        )
        btn_admins_list = InlineKeyboardButton(
            text='Admins list',
            callback_data='admin_settings_list'
        )
        btn_delete_admin = InlineKeyboardButton(
            text='Delete admin',
            callback_data='admin_settings_delete'
        )

        for btn in [btn_add_admin, btn_admins_list,
                    btn_delete_admin, self.btn_back_to_menu]:
            kbd_admin.insert(btn)

        return kbd_admin
