#!/usr/bin/env python3
from circus import get_arbiter


sprogram = {
    "cmd": "python3 stream2db.py",
    "numprocesses": 1,
    "copy_env": True,
    "copy_path" : True
}


arbiter = get_arbiter([sprogram])


try:
    arbiter.start()
finally:
    arbiter.stop()
