# -*- coding=utf-8 -*-

def now():
    import time
    return int(time.time())

def md5(s):
    try:
        from hashlib import md5
    except ImportError:
        from md5 import md5
    return md5(s).hexdigest()   

from ucenter.base import Configs, Ucenter
from ucenter.client import Client
from ucenter.views import UcenterAPI

__all__ = ['Ucenter', 'Configs', 'Client', 'UcenterAPI', 'now', 'md5']
