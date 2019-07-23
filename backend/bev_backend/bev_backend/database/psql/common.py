#!/usr/bin/env python3
import logging
import asyncio
import asyncpg
from bev_backend.utils.config import get_config



async def get_connection():
    config = get_config()
    conn = await asyncpg.connect(
        # TODO: can become configurables in the future
        host='127.0.0.1',
        port=5432,
        user=config['DB']['user'],
        password=config['DB']['password'],
        database=config['DB']['dbname']
    )
    # destroy authentication info ASAP
    del config
    return conn



async def run_sync_transaction(awtable_queries, query_args):
    '''
        awtable_queries : async functions that model PSQL queries
                these functions ALWAYS take connection as first argument
        query_args : dictionaries of named arguments of corresponding functions

        run queries in order SYNChronously
    '''
    conn = await get_connection()
    results = dict()
    try:
        async with conn.transaction():
            for query, args in zip(awtable_queries, query_args):
                result = await query(conn, **args)
                results[query.__name__] = result
    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at {}".format(query.__name__))
        #logging.error("query arguments : {}".format(args))
    finally:
        await conn.close()
        return results



async def singleton_query(query, args):
    conn = await get_connection()
    try:
        output = await query(conn, **args)
    except Exception as e:
        await conn.close()
        raise e
    finally:
        await conn.close()
    return output
