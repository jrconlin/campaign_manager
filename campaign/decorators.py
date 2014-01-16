import json
import pyramid.httpexceptions as http
import random
import utils
from campaign import logger, LOG
from campaign.auth.default import DefaultAuth
from dateutil import parser
from pyramid.request import Request
from pyramid.testing import DummyRequest
from time import time


class checkService(object):
    """ If there is a service flag currently set, don't send out data. """

    def __init__(self, fn=None):
        self.fn = fn

    def checkService(self, req):
        if req.registry.settings.get('service_until', None):
            # When do we expect the service to be done?"
            delay_until = req.registry.settings.get('service_until')
            # plus a bit of fuzz to dither out the herd
            delay_fuzz = int(req.registry.settings.get('service_fuzz', 30))
            try:
                delay_until = max(int(parser.parse(
                    delay_until).strftime('%s')) - int(time()), 0)
            except ValueError, e:
                logger.log(msg="Could not calculate delay: " + str(e),
                           type="error")
                delay_until = 0
            if delay_until > 0:
                delay_until += random.randrange(0, delay_fuzz)
                raise http.HTTPServiceUnavailable(
                    headers={'Retry-After': str(delay_until)})

    def __call__(self, *args, **kw):
        for arg in args:
            if type(arg) is Request:
                self.checkService(arg)
            break
        return self.fn(*args, **kw)


class authorizedOnly(object):

    def __init__(self, fn):
        self.fn = fn
        pass

    def authorized(self, email, request):
        if email is None:
            return False
        settings = request.registry.settings
        try:
            domains = json.loads(settings.get('auth.valid.domains',
                                 '["@mozilla.com", "@mozilla.org"]'))
            result = False
            for valid_domain in domains:
                if email.lower().endswith(valid_domain):
                    result = True
                    break
            if not result:
                return False
            storage = request.registry.get('storage')
            if utils.strToBool(settings.get("db.checkAccount", True)):
                return storage.is_user(email)
            else:
                return True
        except TypeError:
            pass
        except Exception:
            if utils.strToBool(settings.get('dbg.traceback', False)):
                import traceback
                traceback.print_exc()
            if utils.strToBool(settings.get('dbg.break_unknown_exception',
                                            False)):
                import pdb
                pdb.set_trace()
            pass
        return False

    def login(self, request, skipAuth=False):
        params = dict(request.params.items())
        try:
            if (request.json_body):
                params.update(request.json_body.items())
        except ValueError:
            pass
        try:
            uid = request.session.get('uid')
            if uid and self.authorized(uid, request):
                return True
            #config = request.registry.get('config', {})
            auth = request.registry.get('auth', DefaultAuth)
            email = auth.get_user_id(request)
            if email is None:
                return False
            if self.authorized(email, request):
                session = request.session
                session['uid'] = email
                try:
                    session.persist()
                    session.save()
                except AttributeError:
                    pass
            else:
                return False
        except IOError, e:
            raise e
        except http.HTTPServerError, e:
            raise e
        except Exception, e:
            settings = request.registry.settings
            if utils.strToBool(settings.get('dbg.traceback', False)):
                import traceback
                traceback.print_exc()
            if utils.strToBool(settings.get('dbg.break_unknown_exception',
                                            False)):
                import pdb
                pdb.set_trace()
            if logger:
                logger.log(type='error', severity=LOG.ERROR, msg=str(e))
            else:
                import sys
                sys.stderr.write("Auth Error! %s\n", str(e))
            return False
        # User Logged in
        return True

    def __call__(self, *args, **kw):
        for arg in args:
            if isinstance(arg, Request) or isinstance(arg, DummyRequest):
                if self.login(arg):
                    return self.fn(*args, **kw)
        raise http.HTTPUnauthorized(headers={"Refresh": "url=/"})
