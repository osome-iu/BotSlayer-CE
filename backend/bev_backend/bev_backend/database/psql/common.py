#!/usr/bin/env python3
import logging
import asyncio
import asyncpg
from bev_backend.utils.config import get_config



async def get_connection(timeout=60, command_timeout=None):
    config = get_config()
    conn = await asyncpg.connect(
        # TODO: can become configurables in the future
        host='127.0.0.1',
        port=5432,
        user=config['DB']['user'],
        password=config['DB']['password'],
        database=config['DB']['dbname'],
        timeout=timeout,
        command_timeout=command_timeout
    )
    # destroy authentication info ASAP
    del config
    return conn



async def run_transaction(awtable_queries, query_args, conn_args=None):
    '''
        awtable_queries : async functions that model PSQL queries
                these functions ALWAYS take connection as first argument
        query_args : dictionaries of named arguments of corresponding functions

        run queries in order SYNChronously
    '''
    if conn_args is None:
        conn = await get_connection()
    else:
        conn = await get_connection(**conn_args)

    results = dict()
    query = None
    try:
        async with conn.transaction():
            for query, args in zip(awtable_queries, query_args):
                results[query.__name__] = await query(conn, **args)
    except Exception as e:
        logging.exception("transaction failed")
        if query is None:
            logging.error("failed before any query")
        else:
            logging.error("failed at {}".format(query.__name__))
        await conn.close()
        raise e # exit via exception raising

    await conn.close()
    return results



async def run_query(query, args, conn_args=None):
    if conn_args is None:
        conn = await get_connection()
    else:
        conn = await get_connection(**conn_args)

    output = None
    try:
        task = asyncio.create_task(query(conn, **args))
        output = await task
    except Exception as e:
        logging.exception("transaction failed")
        logging.error("failed at {}".format(query.__name__))
        await conn.close()
        raise e # exit via exception raising

    await conn.close()
    return output
