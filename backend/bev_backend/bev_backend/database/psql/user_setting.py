#!/usr/bin/env python3
import logging
import asyncio
from bev_backend.database.psql.common import run_query



USER_SETTINGS = [
    "consumerKey", "consumerSecret",
    "accessToken", "accessTokenSecret",
    "seed", "pinned",
    "user", "location" ]
PASSWORD_SETTING = 'cfgpass'

# Used for hiding twitter keys
USER_SEED = [
    "seed"
]

read_query = '''
SELECT name, valstr FROM config
    WHERE name = $1;
'''
async def read_setting(conn, setting_keys):
    output = dict()
    for key in setting_keys:
        output[key] = await conn.fetch(read_query, key)
    return output


def get_settings(setting_keys):
    try:
        results = asyncio.run(
            run_query(read_setting, {'setting_keys': setting_keys})
        )
    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at reading config table")
        logging.error("query args : {}".format(setting_keys))
        return None
    return {
        rec[0]['name'] : rec[0]['valstr']
        for rec in results.values()
        if len(rec) > 0
    }


def get_user_settings():
    return get_settings(USER_SETTINGS)

def get_user_seed():
    return get_settings(USER_SEED)


def get_password_setting():
    return get_settings([PASSWORD_SETTING])[PASSWORD_SETTING]



write_query = '''
UPDATE config SET
    valstr = $1
    WHERE name = $2
RETURNING 1;
'''
async def write_setting(conn, key_value_dict):
    '''
        key_value_dict: { name_of_setting str : value_of_setting }
    '''
    for name, val in key_value_dict.items():
        await conn.fetch(write_query, val, name)
    return True


def set_settings(key_value_dict):
    results = -1
    try:
        results = asyncio.run(
            run_query(write_setting, {'key_value_dict': key_value_dict})
        )
    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at reading config table")
        logging.error("query args : {}".format(key_value_dict))
    return results


def set_user_settings(user_setting_dict):
    return set_settings(user_setting_dict)


def set_password_setting(new_pw):
    return set_settings({PASSWORD_SETTING: new_pw})
