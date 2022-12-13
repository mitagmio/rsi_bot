import sqlite3 as sl

import os


class UsersDatabaseConnector:
    """connector to database w/ users"""

    def __init__(self, db_file):
        self.db = sl.connect(db_file)
        self.cursor = self.db.cursor()

    def create_table(self):
        """Creates table if not exists."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                                account_name TEXT,
                                api_key TEXT,
                                api_secret TEXT,
                                invest_percent TEXT,
                                strategy_name TEXT,
                                leverage DECIMAL,
                                margin BOOLEAN,
                                testnet BOOLEAN,
                                bot_on BOOLEAN
                                )''')
        self.db.commit()

    def create_new_user(self, data):
        """Creates new user."""
        try:
            self.cursor.execute(f'''INSERT INTO accounts VALUES 
                        ('{data['friendly_name']}', '{data['api_key']}', '{data['api_secret']}', '{data['invest_percent']}', '', '{data['Leverage']}', {data['Margin']}, False,False)''')
            self.db.commit()
        except Exception as err:
            print(err)

    def get_list_of_users(self):
        """Returns list of users."""
        self.cursor.execute('''SELECT * FROM accounts''')
        data = self.cursor.fetchall()
        accounts_list = []
        for el in data:
            accounts_list.append(el[0])
        return accounts_list

    def get_users_all_data(self):
        """Returns all users data."""
        self.cursor.execute('''SELECT * FROM accounts''')
        data = self.cursor.fetchall()

        return data

    def delete_user(self, account_name):
        """Delete user by name."""
        self.cursor.execute(f"DELETE FROM accounts WHERE account_name = '{account_name}'")
        self.db.commit()

    def get_users_info(self, account_name):
        """Returns user info by name."""
        self.cursor.execute(f'''SELECT * FROM accounts WHERE account_name = "{account_name}"''')
        data = self.cursor.fetchone()

        return data

    def change_invest_for_user(self, account_name, invest_percent):
        """Change invest procent for user by name."""
        self.cursor.execute(
            f'''UPDATE accounts set invest_percent = "{invest_percent}" WHERE account_name = "{account_name}" ''')
        self.db.commit()

    def change_strategy_for_user(self, account_name, strategy_name):
        """Change invest procent for user by name."""
        self.cursor.execute(
            f'''UPDATE accounts set strategy_name = "{strategy_name}" WHERE account_name = "{account_name}" ''')
        self.db.commit()

    def change_bot_on_for_user(self, account_name, bot_on: bool):
        """Change invest procent for user by name."""
        self.cursor.execute(
            f'''UPDATE accounts set bot_on = {bot_on} WHERE account_name = "{account_name}" ''')
        self.db.commit()

    def change_testnet_for_user(self, account_name, testnet: bool):
        """Change invest procent for user by name."""
        self.cursor.execute(
            f'''UPDATE accounts set testnet = {testnet} WHERE account_name = "{account_name}" ''')
        self.db.commit()


class BotConfiguration:
    """Connector to configuration."""

    def __init__(self, db_file):
        self.db = sl.connect(db_file)
        self.cursor = self.db.cursor()

    def create_table(self):
        """ creates table if not exists """
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bot_config (
                                name TEXT,
                                sma BOOLEAN,
                                len_rsi DECIMAL,
                                len_sma DECIMAL,
                                long_entry DECIMAL,
                                long_exit DECIMAL,
                                short_entry DECIMAL,
                                short_exit DECIMAL,
                                timeframe DECIMAL,
                                upd_timeframe DECIMAL,
                                symbols TEXT,
                                buy_more_times DECIMAL
                                )''')
        self.db.commit()
        # qty_reduce_per_order REAL

    def get_strategy(self):
        """Returns current strategy"""
        self.cursor.execute("""SELECT * FROM bot_config""")
        res = self.cursor.fetchall()

        return res

    def get_strategy_info(self, name):
        """Returns user info by name."""
        self.cursor.execute(f'''SELECT * FROM bot_config WHERE name = "{name}"''')
        data = self.cursor.fetchone()

        return data

    def delete_strategy(self, name):
        """Delete user by name."""
        self.cursor.execute(f"DELETE FROM bot_config WHERE name = '{name}'")
        self.db.commit()

    def get_list_of_strategies(self):
        """Returns list of users."""
        self.cursor.execute('''SELECT * FROM bot_config''')
        data = self.cursor.fetchall()
        accounts_list = []
        for el in data:
            accounts_list.append(el[0])
        return accounts_list

    def update_table(self, data: dict):  # todo
        """Change strategy by list"""
        self.cursor.execute(f'''INSERT INTO bot_config VALUES 
            (
            '{str(data['name'])}', 
            {bool(data['rsi_sma'])}, 
            {int(data['len_rsi'])},
            {int(data['len_sma'])},
            {int(data['long_entry'])},
            {int(data['long_exit'])},
            {int(data['short_entry'])},
            {int(data['short_exit'])},
            {int(data['timeframe'])},
            {int(data['upd_timeframe'])},
            '{str(data['symbols'])}',
            '{int(data['buy_more_times'])}'
            )''')
        self.db.commit()
    def get_symbols(self, name_strategy:str)->str:
        ans = self.cursor.execute('SELECT symbols FROM bot_config WHERE name=?', [name_strategy]).fetchone()
        return ans[0]


class AdminDatabaseConnector:
    """Connector to admins database."""

    def __init__(self, db_file):
        self.db = sl.connect(db_file)
        self.cursor = self.db.cursor()

    def create_table(self):
        """Creates table if not exists."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                                user_id TEXT PRIMARY KEY
                                )''')
        self.db.commit()

    def get_admins_list(self):
        """Returns admins list."""
        self.cursor.execute('''SELECT * FROM admins''')
        data = self.cursor.fetchall()
        self.db.commit()
        return data

    def add_admin(self, user_id):
        """Add new admin."""
        self.cursor.execute(f'''INSERT INTO admins VALUES ('{user_id}')''')
        self.db.commit()

    def delete_admin(self, user_id):
        """Delete admin by id."""
        self.cursor.execute(f"DELETE FROM admins WHERE user_id = '{user_id}'")
        self.db.commit()


class BotSwitch:
    """Here will be one var, where will be info about bot ON, or bot OFF"""

    def __init__(self, db_file):
        self.db = sl.connect(db_file)
        self.cursor = self.db.cursor()

    def create_table(self):
        """ creates table if not exists """
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bot (status BOOLEAN)''')
        self.db.commit()

    def bot_status(self):
        """Return bot status, default None, so we need to make it False before
        return."""
        try:
            self.cursor.execute('''SELECT status FROM bot''')
            data = self.cursor.fetchone()[0]
            if data is None:
                self.insert_bot(value=False)
                self.bot_status()
            else:
                return data
        except TypeError:
            self.insert_bot(value=False)
            self.bot_status()

    def insert_bot(self, value: bool):
        """Insert new line."""
        self.cursor.execute(f'''INSERT INTO bot VALUES ( {value})''')
        self.db.commit()

    def change_bot_status(self, value: bool):
        """Change bot status."""
        self.cursor.execute(f'''UPDATE bot set status = {value}''')
        self.db.commit()


homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-2])
try:
    db_users = UsersDatabaseConnector(f'..{homeDir}/DBs/users.db')
    db_settings = BotConfiguration(f'..{homeDir}/DBs/settings.db')
    db_admin = AdminDatabaseConnector(f'..{homeDir}/DBs/admins.db')
except:
    db_users = UsersDatabaseConnector(f'{homeDir}/DBs/users.db')
    db_settings = BotConfiguration(f'{homeDir}/DBs/settings.db')
    db_admin = AdminDatabaseConnector(f'{homeDir}/DBs/admins.db')

for db in [db_users, db_settings, db_admin]:  # Create tables for all connectors if not exist.
    db.create_table()
