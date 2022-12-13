from database_connector import db_users, db_settings


def get_data_from_telegram() -> dict:
    """return dict w/ all data from databases"""
    data = \
        {
            'bot_status': True if db_bot_switch.bot_status() == 1 else False,
            'users': [],
            'settings': []
        }

    settings = db_settings.get_strategy()

    for el in settings:
        data['settings'].append({
            'take_id': el[0],
            'breakeven': True if el[1] == 1 else False,
            'qty_reduce': float(el[2])
        }
        )

    users = db_users.get_users_all_data()

    for user in users:
        data['users'].append(
            {
                'frendly_name': user[0],
                'api_key': user[1],
                'api_secret': user[2],
                'invest_part': user[3]
            }
        )

    return data
