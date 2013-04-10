# -*- coding=utf-8 -*-

import urllib2
import os.path
from urllib import urlencode
from xml.dom.minidom import parseString
import functools

from ucenter import *

def generate_interfaces():
    import yaml
    with open(os.path.join(os.path.dirname(__file__), 'uc_client.yaml'), 'r') as f:
        return yaml.load(f)
interfaces = generate_interfaces()

class UcenterError(Exception):
    errors = ('Access denied for agent changed',
            'Module not found!',
            'Action not found!')


class Client(object):
    def __init__(self, user_agent):
        self._user_agent = user_agent

    def uc_api_post(self, module, action, **kwargs):
        postdata = urlencode(self.uc_api_requestdata(module, action, kwargs))
        return self._uc_remote(Configs.UC_API+'/index.php', postdata)

    def uc_api_url(self, module, action, **kwargs):
        getdata = urlencode(self.uc_api_requestdata(module, action, kwargs))
        return Configs.UC_API + '/index.php?' + getdata

    def uc_api_requestdata(self, module, action, data):
        return {'m': module, 'a': action, 'inajax': 2,
                'release': Configs.UC_CLIENT_RELEASE, 'appid': Configs.UC_APPID,
                'input': self.uc_api_input(data)}

    def uc_api_input(self, data):
        data['agent'] = md5(self._user_agent)
        data['time'] = str(now())
        return Ucenter.authcode_encode(urlencode(data), Configs.UC_KEY)

    def _uc_remote(self, url, data):
        req = urllib2.Request(url)
        req.add_header('Accept', '*/*')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('User-Agent', self._user_agent)
        req.add_header('Cache-Control', 'no-cache')
        req.add_header('Cookie', '')

        response = urllib2.urlopen(req, data)
        result = response.read()
        if result in UcenterError.errors:
            raise UcenterError, result
        return result

    def array(self, result):
        try:
            dom = parseString(result)
            return map(self.number_or_string,
                    [x.firstChild.data for x in dom.getElementsByTagName('item')])
        except:
            return self.number_or_string(result)

    def number_or_string(self, x):
        return int(x) if x.isdigit() else x

    def __getattr__(self, name):
        ifname = name.split('_', 2)
        if ifname[0] != 'uc':
            raise AttributeError, '\'Client\' object has no attribute \'%s\'' % name

        def _ucwrapper(**kwargs):
            if not ucif:
                raise NotImplementedError, name
            try:
                if ucif['args']:
                    kw = dict(ucif['args'])
                else:
                    kw = dict()
                kw['module'] = ucif['module']
                kw['action'] = ucif['action']
                for k in kwargs.keys():
                    if not kw.has_key(k):
                        raise KeyError, k
                    kw[k] = kwargs[k]
                    if isinstance(kw[k], unicode):
                        kw[k] = kw[k].encode('utf-8')
                if ucif['return'] == 'url':
                    return self.uc_api_url(**kw)
                if ucif['return'] == 'array':
                    fn = self.array
                else:
                    fn = self.number_or_string
                return fn(self.uc_api_post(**kw))
            except KeyError, e:
                raise TypeError, '\'%s\' is not an invalid keyword argument for this function' % e

        for ucif in interfaces:
            if ifname[1] == ucif['module'] and ifname[2] == ucif['action']:
                return _ucwrapper
        raise AttributeError, '\'Client\' object has no attribute \'%s\'' % name
