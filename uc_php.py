# -*- coding=utf-8 -*-

from ucenter import *
import urlparse

class UcenterAPI(object):
    API_RETURN_SUCCEED = '1'
    API_RETURN_FAILED = '-1'
    API_RETURN_FORBIDDEN = '-2'
    API_INVALID = 'Invalid Request'
    API_AUTH_EXPIRED = 'Authracation has expiried'

    def parse_args(self, qs):
        qs = urlparse.parse_qs(qs)
        for k in qs.keys():
            qs[k] = qs[k][0]
        return qs

    def __call__(self, code):
        qs = self.parse_args(Ucenter.authcode_decode(code, Configs.UC_KEY))
        if not qs:
            return self.API_INVALID
        try:
            if now() - int(qs['time']) > 3600:
                return self.API_AUTH_EXPIRED
        except KeyError:
            return self.API_INVALID
        except ValueError:
            return self.API_INVALID

        try:
            uc_php = getattr(self, 'do_' + qs['action'], None)
            if not uc_php:
                return self.API_RETURN_FORBIDDEN
            return uc_php(**qs)
        except KeyError:
            return self.API_INVALID
        except NotImplementedError:
            return self.API_RETURN_FORBIDDEN
        except:
            return self.API_INVALID

    def do_test(self, **kwargs):
        return self.API_RETURN_SUCCEED

    def do_synlogin(self, **kwargs):
        raise NotImplementedError

    def do_synlogout(self, **kwargs):
        raise NotImplementedError
