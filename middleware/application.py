#!/usr/bin/env python3
# Flask app whose primary purpose is to serve the frontend
import re
import os
import sys
import time
import asyncio
import subprocess
from os import path, statvfs
from datetime import datetime, timedelta
'''
    Dependencies
'''
import asyncpg
import requests
import flask_wtf
import pandas as pd             # for bs_k_core function
import networkx as nx           # for bs_k_core function
try:
    import simplejson as json
except ImportError:
    import json
from flask import Flask, render_template, request, abort, jsonify, send_from_directory, make_response
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect, validate_csrf, generate_csrf
from flask_caching import Cache
from concurrent.futures._base import TimeoutError as DBTimeoutError
from bev_backend.utils.config import get_config
from bev_backend.utils.version import __version__
from bev_backend.database.psql.user_setting import get_user_seed
from bev_backend.database.psql.user_setting import get_user_settings
from bev_backend.database.psql.user_setting import set_user_settings
from bev_backend.database.psql.user_setting import get_password_setting
from bev_backend.database.psql.user_setting import set_password_setting
from bev_backend.database.psql.web_content import get_timeline
from bev_backend.database.psql.web_content import get_hoaxy_data
from bev_backend.database.psql.web_content import get_coord_score_report



'''
    Setup logging
'''
import logging
logging.getLogger('flask_cors').level = logging.DEBUG
logging.getLogger('flask_wtf.csrf').level = logging.INFO



'''
    Check the required directory structure
'''
# buffer for build delay, allow 30s delay
retrial = 0
while not path.isfile("./frontend/index.html"):
    time.sleep(10)
    retrial += 1

    if retrial >= 3:
        # frontend absent
        logging.error("Server cannot start. Frontend does not exist. " +
                      "../frontend/dist does not exist.")
        logging.error("Go to frontend directory and run 'npm run build' "+
                      "to build the frontend.")
        raise SystemExit("frontend doesn't exist")



'''
    Declare global objects and main function
'''
# setting up the app
SECRET_KEY = os.urandom(32)
application = app = Flask(__name__,
    template_folder="./frontend",
    static_folder="./frontend/assets",
)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['WTF_CSRF_ENABLED'] = True
app.config['CSRF_ENABLED'] = True
app.config['WTF_CSRF_CHECK_DEFAULT'] = True
CORS(app)
# setting up CSRF token
csrf = CSRFProtect()
csrf.init_app(app)
# setting up
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)



'''
    Main function (entrypoint)
'''
def main():
    config = get_config('./config.ini')
    try:
        application.run(
            host=config['MIDDLEWARE']['host'],
            port=config['MIDDLEWARE']['port'],
            debug=config['MIDDLEWARE']['debug']
        )
    except Exception as e:
        logging.exception("Excecption fell through all catches.")
        raise SystemExit


def datetime_str(dt_str):
    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S').replace(
        second=0, microsecond=0 # resolution in minutes
    )

def utcnow_in_min():
    return datetime.utcnow().replace(second=0,microsecond=0)


'''
    Helper functions
'''
def datetime_str(dt_str):
    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S').replace(
        second=0, microsecond=0 # resolution in minutes
    )

def utcnow_in_min():
    return datetime.utcnow().replace(second=0, microsecond=0)



'''
    Cached wrappers for DB queries
'''
@cache.memoize(timeout=60)
def timeline_wrapper(target_entity_ids, ref_time):
    target_entity_ids = target_entity_ids.split(',')
    try:
        return jsonify(get_timeline(entity_ids=target_entity_ids, ref_time=ref_time))
    except DBTimeoutError as e:
        return jsonify([{"timeout": True}]), 500


@cache.memoize(timeout=60)
def hoaxy_data_wrapper(entity_ids, ref_time):
    entity_ids = entity_ids.split(',')
    try:
        results = get_hoaxy_data(entity_ids=entity_ids, ref_time=ref_time)
    except DBTimeoutError as e:
        return jsonify([{"timeout": True}]), 500

    url_template = "https://twitter.com/{}/status/{}"
    try:
        toJSONArray = [
            {
                "canonical_url": "",
                "date_published": (row['tweet_date']).isoformat(),
                "domain": "",
                "from_user_botscore":
                    row['from_user_botscore']
                        if row['from_user_botscore'] > 0.00001
                        else 0.00001,
                "from_user_id": row['from_user_id'],
                "from_user_screen_name": row['from_user_screenname'],
                "is_mention": 'FALSE',
                "original_query": "",
                "pub_date": (row['tweet_date']).isoformat(),
                "site_domain": "",
                "site_type": "claim",
                "title": "",
                "to_user_botscore":
                    row['to_user_botscore']
                        if row['to_user_botscore'] > 0.00001
                        else 0.00001,
                "to_user_id": row['to_user_id'],
                "to_user_screen_name": row['to_user_screenname'],
                "tweet_created_at": (row['tweet_date']).isoformat(),
                "tweet_id": row['tid'],
                "tweet_type": row['tweet_type'],
                "tweet_url":
                    url_template.format(row['from_user_screenname'], row['tid'])
                        if row['tweet_type']=='reply'
                    else url_template.format(row['to_user_screenname'], row['tid']),
                "url_id": "",
                "url_raw": "",
            }
            for row in results
        ]
    except:
        return jsonify([{"error": "Likely timed out while trying to query the DB."}]), 500

    if(len(toJSONArray) > 0):
        column_names = list(toJSONArray[0].keys())

        df = pd.DataFrame.from_records(
            [tuple(ele.values()) for ele in toJSONArray]
            , columns=column_names
        )

        if (len(df) >= 1500):
            filtered_df = bs_k_core(df,
                from_col_name="from_user_id", to_col_name="to_user_id",
                nodes_limit=1500)
        else:
            filtered_df = df

        toJSONArray = [
            {
                col : row[col]
                for col in column_names
            }
            for idx, row in filtered_df.iterrows()
        ]

        return jsonify(toJSONArray)

    else:
        return jsonify([{"no_data": True}])


@cache.memoize(timeout=60)
def coord_score_report_wrapper(exclusion, ref_time):
    exclusion_set = { # a set for exclusion
        entity[1:].lower() if entity[0] in MAIN_ENTITY_PREFIX
            else entity
        for entity in exclusion.strip(', ').split(",")
        if len(entity) > 0
    }

    # requested_time = request.args.get('time', default=datetime.utcnow(), type = str)
    # # print(requested_time)

    ref_time = request.args.get('time', default=utcnow_in_min(), type=datetime_str)

    try:
        # records = get_coord_score_report(ref_time=requested_time)
        records = get_coord_score_report(ref_time=ref_time)
    except asyncpg.exceptions.DivisionByZeroError as e:
        # return early for division by zero
        return jsonify([{"insufficient_data": True}])
    except DBTimeoutError as e:
        return jsonify([{"timeout": True}]), 500

    toJSONArray = []

    for row in records:
        # filter query seed if needed
        entity_text = row['entity_text']
        if entity_text in exclusion_set:
            continue

        # append appropriate prefix
        entity_type = row['entity_type']
        symbol_prefix = ''
        if (entity_type == "hashtags"):
            symbol_prefix = '#'
        elif (entity_type == "user_mentions"):
            symbol_prefix = '@'
        elif (entity_type == "symbols"):
            symbol_prefix = '$'

        # media link from a join in PSQL
        media_link = row['media_link']
        media_link = '' if media_link is None else media_link

        # format elements
        toJSONArray.append(
            {
                "Entity": symbol_prefix+entity_text,
                "Last_Seen": row['last_seen'],
                "Tweets": row['twt_cnt'],
                "Botness": '%.1f' % (float(row['mean_bs']) * 5.0),
                "BS_Level": '%.3f' % (row['coord_score']),
                "Type": entity_type,
                "Trendiness": '%d' % int((float(row['trend']) - 1.0) * 100),
                "Accounts": row['acc_cnt'],
                "MediaLink": media_link,
                "EntityID": row['entity_id']
            }
        )

    return jsonify(toJSONArray)



'''
===================
    APIs below
===================
'''

'''
    INDEX
'''
@application.route("/")
def index():
    resp = make_response(render_template("/index.html"))
    resp.headers['X-Robots-Tag'] = 'noindex'
    return resp

@application.route("/<path:fallback>")
def fallback(fallback):
    resp = make_response(render_template("/index.html"))
    resp.headers['X-Robots-Tag'] = 'noindex'
    return resp

'''
    PASSWORD SETTING
'''
@application.route("/api/changePass")
def change_password():
    token = request.headers.get("X-CSRFToken")
    validate_csrf(token)
    new_pass = request.args.get('newPass', default=' ', type = str)
    set_password_setting(new_pass)
    return "All clear"

@application.route("/api/checkPass")
def check_password():
    token = request.headers.get("X-CSRFToken")
    validate_csrf(token)
    pass_attempt = request.args.get('currentPass', default=' ', type = str)
    correct_pass = get_password_setting()

    if(correct_pass == 'password_not_set'):
        return 'firstTime'

    if(pass_attempt == correct_pass):
        return 'true'
    else:
        return 'false'


'''
    OTHER USER SETTINGS
'''
def jsonify_user_settings():
    output = jsonify(get_user_settings())
    return output

def jsonify_user_seed():
    output = jsonify(get_user_seed())
    return output

@application.route("/api/configReadSeed")
def config_read_seed_ep():
    return jsonify_user_seed()

@application.route("/api/configRead")
def config_read_ep():
    token = request.headers.get("X-CSRFToken")
    validate_csrf(token)
    return jsonify_user_settings()

@application.route("/api/getExclusions")
def get_exclusions():
    config_dict = jsonify_user_settings()

@application.route("/api/configSave")
def config_ini_save():
    token = request.headers.get("X-CSRFToken")
    validate_csrf(token)
    user_settings = get_user_settings()
    set_user_settings({
        setting_key : request.args.get(setting_key, default="", type=str).strip()
        for setting_key in user_settings.keys()
    })

    subprocess.run("circusctl restart python3 &", shell=True)
    return "All quiet on the western front"


'''
    LOGS
'''
@application.route("/api/streamErrors")
def jsonify_stream_errors():
    errors = {
        'stream_error': '',
        'stream_date_time': '',
    }

    try:
	    with open('../stream.log', 'r') as f:
	        for line in f:
	            if 'Error, code' in line:
	                current_datetime = datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S')
	                if (datetime.now() - current_datetime).total_seconds() < 86400:
	                    tmp_line = line
	                    errors['stream_date_time'] = line[:19]
	                    errors['stream_error'] = line[39:-1]

    except Exception as e:
    	errors['stream_error'] = "Stream log does not exist"
    	errors['stream_date_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify([errors])

@application.route("/api/dbErrors")
def jsonify_db_errors():
    errors = {
        'db_error': '',
        'db_date_time': '',
    }
    try:
	    with open('../db.log', 'r') as f:
	        for line in f:
	            if line[0].isdigit():
	                if 'exit code 1' in line:
	                    current_datetime = datetime.strptime(line[:23], '%Y-%m-%d %H:%M:%S.%f')
	                    if (datetime.now()-current_datetime).total_seconds() < 86400:
	                        errors['db_date_time'] = line[:23]
	                        errors['db_error'] = line[38:]

    except Exception as e:
    	errors['db_error'] = "Database log does not exist"
    	errors['db_date_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify([errors])

@application.route("/api/serverErrors")
def jsonify_server_errors():
    errors = {
        'server_error': '',
        'server_date_time': '',
    }

    try:
	    with open('../server.log', 'r') as f:
	        for line in f:
	            if line[0].isdigit():
	                if int(re.findall(r'\D(\d{3})\D', line)[-1]) >= 500:
	                    current_datetime = datetime.strptime(line[16:36], '%d/%b/%Y %H:%M:%S')
	                    if (datetime.now() - current_datetime).total_seconds() < 86400:
	                        errors['server_date_time'] = line[16:36]
	                        errors['server_error'] = line[38:]

    except Exception as e:
    	errors['server_error'] = "Server log does not exist"
    	errors['server_date_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify([errors])



'''
    BACKEND CALLBACKS
'''
# Not currently working. May return in beta, so commenting out.
# @application.route("/api/pauseCollection")
# def pause_collection():
#     subprocess.run("circusctl stop python3 &", shell=True)
#     return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@application.route("/api/diskSpace")
def get_disk_space():
    st = statvfs('/')
    avail = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    percent = avail * 1.0 / total * 100.0
    return str(percent)


@application.route("/api/localVersion")
def get_local_version():
    return __version__

MAIN_ENTITY_PREFIX = {'#', '@', '$'}
@application.route("/api/scoreDemo")
def score_demo():
    exclusion = request.args.get('exclusion', default=' ', type = str)
    ref_time = request.args.get('time', default=utcnow_in_min(), type = datetime_str)
    return coord_score_report_wrapper(exclusion, ref_time)

@application.route("/api/timeline")
def access_timeline():
    target_entity_ids = request.args.get('entityIDs', default='', type = str)
    ref_time = request.args.get('time', default=utcnow_in_min, type=datetime_str)
    return timeline_wrapper(target_entity_ids, ref_time)

@application.route("/api/sendToHoaxy")
def send_to_hoaxy():
    # Hoaxy logic:
    # https://github.com/IUNetSci/hoaxy-backend/blob/master/hoaxy/ir/search.py#L570
    entity_ids = request.args.get('entityIDs', default='', type = str)
    ref_time = request.args.get('time', default=utcnow_in_min, type=datetime_str)
    return hoaxy_data_wrapper(entity_ids, ref_time)



def bs_k_core(df, from_col_name, to_col_name,
                nodes_limit=None, edges_limit=None):
    """
    Use k_core method to remove less import nodes and edges.
    Parameters
    ----------
    df : pandas.DataFrame
        The edges dataframe.
    from_col_name: str
        the name of the column representing from node in an edge
    to_col_name: str
        the name of the column representing to node in an edge
    nodes_limit : int
        The maximum number of nodes to return.
    edges_limit : int
        The maximum number of edges to return.
    Returns
    -------
    pandas.DataFrame
        This dataframe is refined with k_core algorithm.
    """
    v_cols = [from_col_name, to_col_name]
    G = nx.from_pandas_edgelist(
        df, v_cols[0], v_cols[1], create_using=nx.DiGraph())
    G.remove_edges_from(nx.selfloop_edges(G))
    # if G.number_of_nodes() == 1:
    #     raise ValueError("Only one node in the network. Nothing to visualize")
    #
    # sort nodes by ascending core number
    core = nx.core_number(G)
    nodes_list = sorted(list(core.items()), key=lambda k: k[1], reverse=False)
    nodes_list = list(zip(*nodes_list))[0]
    nodes_list = list(nodes_list)
    #
    # if there are no nodes in excess, do not execute
    excess_nodes = G.number_of_nodes() - nodes_limit
    if nodes_limit and excess_nodes > 0:
        nodes_to_remove = nodes_list[:excess_nodes]
        nodes_list = nodes_list[excess_nodes:]
        G.remove_nodes_from(nodes_to_remove)
    #
    # remove nodes in batches until the the number of edges is below the
    # limit. Only execute if edges_limit argument is passed (not None) and
    # is positive
    if edges_limit:
        batch_size = 10
        while G.number_of_edges() > edges_limit:
            nodes_to_remove = nodes_list[:batch_size]
            nodes_list = nodes_list[batch_size:]
            G.remove_nodes_from(nodes_to_remove)

    df = df.set_index([from_col_name, to_col_name])
    filtered_df = df.loc[list(G.edges())]
    return filtered_df.reset_index()



if __name__ == '__main__': main()
