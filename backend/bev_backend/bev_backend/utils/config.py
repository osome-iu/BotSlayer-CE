import copy
import configparser



CONFIG = {
    'DB': {
        'dbname'   : 'bev',
        'user'     : 'bev',
        'password' : 'bev'
    },
    'MIDDLEWARE':{
        'debug' : True,
        'port'  : 5000,
        'host'  : '0.0.0.0'
    }
}



def get_config(fpath='/root/bev/config.ini'):
    return copy.deepcopy(CONFIG)
