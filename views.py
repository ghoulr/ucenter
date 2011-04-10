# -*- coding=utf-8 -*-

from django.http import HttpResponse

from ucenter import *
import urlparse

class UcenterAPI(object):
    API_RETURN_SUCCEED = '1'
    API_RETURN_FAILED = '-1'
    API_RETURN_FORBIDDEN = '-2'

    def parse_args(self, qs):
        qs = urlparse.parse_qs(qs)
        for k in qs.keys():
            qs[k] = qs[k][0]
        return qs

    def __call__(self, request):
        code = request.REQUEST.get('code', '')
        qs = self.parse_args(Ucenter.authcode_decode(code, Configs.UC_KEY))
        if not qs:
            return HttpResponse('Invalid Request')
        try:
            if now() - int(qs['time']) > 3600:
                return HttpResponse('Authracation has expiried')
        except KeyError:
            return HttpResponse('Invalid Request')
        except ValueError:
            return HttpResponse('Invalid Request')

        try:
            uc_php = getattr(self, 'do_' + qs['action'], None)
            if not uc_php:
                return HttpResponse(self.API_RETURN_FORBIDDEN)
            self._request = request
            return HttpResponse(uc_php(**qs))
        except KeyError:
            return HttpResponse('Invalid Request')
        except NotImplementedError:
            return HttpResponse(self.API_RETURN_FORBIDDEN)
        except:
            return HttpResponse('Invalid Request')

    def do_test(self, **kwargs):
        return self.API_RETURN_SUCCEED
