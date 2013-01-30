# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
""" Cornice services.
"""
from campaign import logger, LOG
from decorators import checkService, authorizedOnly
from mako.template import Template
from mozsvc.metrics import Service
from webob import Response
from campaign.util import strToUTC
import json
import os
import pyramid.httpexceptions as http
import time


api_version = 1

fetch = Service(name='fetch',
                path='/announce/%s/{product}/{channel}/{version}/{platform}' %
                api_version,
                description='Fetcher')
get_all = Service(name="get_all",
                  path='/announce/',
                  description='Fetch Everything')
author2 = Service(name='author2',
                  path='/author/%s/{id}' % api_version,
                  description='Authoring Interface with record')
author = Service(name='author',
                 path='/author/%s/' % api_version,
                 description='Authoring Interface')
logout = Service(name='logout',
                 path='/logout/',
                 description='logout')
redirl = Service(name='redir2',
                 path='/redirect/%s/{locale}/{token}' % api_version,
                 description='redir with locale')
redir = Service(name='redir',
                path='/redirect/%s/{token}' % api_version,
                description='redir')
health = Service(name='health',
                 path='/status/',
                 description='Health Check')
root = Service(name='root',
               path='/',
               description='Default path')

_TMPL = os.path.join(os.path.dirname(__file__), 'templates')


def get_lang_loc(request):
    header = request.headers.get('Accept-Language', 'en-US')
    langloc = header.split(',')[0]
    if ('-' in langloc):
        (lang, loc) = langloc.split('-')
    elif ('_' in langloc):
        (lang, loc) = langloc.split('_')
    else:
        (lang, loc) = (langloc, None)
    if loc:
        loc = loc.upper()
    return {'lang': lang.lower(), 'locale': loc}


def get_last_accessed(request):
    last_accessed = None
    try:
        if 'If-Modified-Since' in request.headers:
            last_accessed_str = request.headers.get('If-Modified-Since')
            last_accessed = strToUTC(last_accessed_str)
            # pop off tz adjustment (in seconds)
            if request.registry['logger']:
                ims_str = time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                                        time.gmtime(last_accessed))
                request.registry['logger'].log(type='campaign',
                                               severity=LOG.DEBUG,
                                               msg='I-M-S: %s (%s)' %
                                                   (ims_str,
                                                       last_accessed_str),
                                               fields={})
    except Exception, e:
        settings = request.registry.settings
        if settings.get('dbg.traceback', False):
            import traceback
            traceback.print_exc()
        if settings.get('dbg.break_unknown_exception', False):
            import pdb
            pdb.set_trace()
        request.registry['logger'].log(type='error',
                                       severity=LOG.ERROR,
                                       msg='Exception: %s' % str(e))
    return {'last_accessed': last_accessed}


def log_fetched(request, reply):
    rlogger = request.registry['logger']
    rlogger.log(type='log',
                severity=LOG.NOTICE,
                msg='fetched',
                fields=json.dumps(reply['announcements']))


@fetch.get()
@checkService
def get_announcements(request, now=None):
    """Returns campaigns in JSON."""
    # get the valid user information from the request.
    rlogger = request.registry.get('logger')
    storage = request.registry.get('storage')
    if not isinstance(request.GET, dict):
        args = dict(request.GET)
    else:
        args = request.GET
    args.update(request.matchdict)
    args.update(get_lang_loc(request))
    last_accessed = get_last_accessed(request)
    args.update(last_accessed)
    try:
        reply = {'announcements': storage.get_announce(args, now)}
    except Exception, e:
        rlogger.log(type='log', severity=LOG.ERROR,
                    msg='EXCEPTION: %s' % str(e))
        raise http.HTTPServerError

    args.update({'useragent': request.user_agent})
    rlogger.log(type='log', severity=LOG.NOTICE,
                msg='fetch_query', fields=args)
    if not len(reply['announcements']):
        if last_accessed.get('last_accessed'):
            raise http.HTTPNotModified
        else:
            raise http.HTTPNoContent
    log_fetched(request, reply)
    response = Response(json.dumps(reply))
    timestamp = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                              time.gmtime())
    # The client will echo back in If-Modified-Since whatever we provide
    # in the Date header
    response.headerlist = [
        ('Content-Type', 'application/json; charset=UTF-8'),
        ('Date', timestamp)]
    return response


def get_template(name):
    name = os.path.join(_TMPL, '%s.mako' % name)
    try:
        return Template(filename=name)
    except IOError, e:
        logger.error(str(e))
        raise http.HTTPServerError


def get_file(name):
    try:
        name = os.path.abspath(os.path.join(_TMPL, name))
        if name.startswith(_TMPL):
            ff = open(name)
            return ff.read()
    except IOError:
        pass
    raise http.HTTPNotFound


@get_all.get()
@authorizedOnly
def get_all_announcements(request):
    storage = request.registry.get('storage')
    tdata = {"announcements": storage.get_all_announce()}
    return tdata


@author.get()
@author2.get()
def admin_page(request, error=None):
    if request.registry.settings.get('auth.block_authoring', False):
        raise http.HTTPNotFound()
    auth = authorizedOnly(None)
    if not auth.login(request):
        return login_page(request)
    tdata = get_all_announcements(request)
    tdata['author'] = request.session['uid']
    tdata['error'] = error
    tdata['settings'] = request.registry.settings
    try:
        if 'javascript' in request.accept_encoding:
            if not error:
                raise http.HTTPOk
            raise http.HTTPConflict(json.dumps(error))
    except AttributeError:
        pass
    template = get_template('main')
    content_type = 'text/html'
    reply = template.render(**tdata)
    response = Response(reply, content_type=content_type)
    return response


# sad to use post for DELETE, but JQuery doesn't add args to DELETE for bulk.
@author.post()
@author2.post()
@authorizedOnly
def manage_announce(request):
    args = request.params.copy()
    args.update(request.matchdict)
    if request.registry.settings.get('auth.block_authoring', False):
        raise http.HTTPNotFound()
    # Clean up the login info
    try:
        del args['assertion']
        del args['audience']
    except KeyError:
        pass
    storage = request.registry.get('storage')
    settings = request.registry.settings
    session = request.session
    err = None
    if 'delete' in args or 'delete[]' in args:
        try:
            del_announce(request)
        except http.HTTPOk:
            pass
        except http.HTTPNotFound, e:
            pass
        return admin_page(request)
    try:
        if args is not None and len(args) > 0:
            if not args.get('author'):
                args['author'] = session.get('uid')
            storage.put_announce(args)
    except Exception, e:
        if settings.get('dbg.traceback', False):
            import traceback
            traceback.print_exc()
        if settings.get('dbg.break_unknown_exception', False):
            import pdb
            pdb.set_trace()
        # display error page.
        err = {'code': 1,
               'error': str(e)}
        pass
    return admin_page(request, err)


@author.delete()
@authorizedOnly
def del_announce(request):
    storage = request.registry.get('storage')
    args = dict(request.params)
    args.update(request.matchdict)
    deleteables = args.get('delete', args.get('delete[]', '')).split(',')
    if len(deleteables):
        storage.del_announce(deleteables)
    raise http.HTTPOk


@root.get()
def boot_to_author(request):
    raise http.HTTPTemporaryRedirect(location='/author/%s/' % api_version)


@logout.delete()
def logout_page(request):
    session = request.session
    if 'uid' in session:
        del session['uid']
        try:
            session.persist()
            session.save()
        except AttributeError:
            pass


def login_page(request, error=None):
    session = request.session
    try:
        if 'javascript' in request.accept_encoding:
            # Don't display the login page for javascript requests.
            if not error:
                raise http.HTTPForbidden
            raise http.HTTPInternalServerError(str(error))
    except AttributeError:
        pass
    try:
        template = get_template('login')
        # use 'invalid@nowhere' to break persona looping on logout.
        response = Response(str(template.render(
            user=session.get('uid', 'invalid@nowhere'),
            audience=request.environ.get('HTTP_HOST'))),
            status=403)
        if (session.get('uid')):
            del(session['uid'])
        try:
            session.persist()
            session.save()
        except AttributeError:
            pass  # because testing
        return response
    except Exception, e:
        settings = request.registry.settings
        if settings.get('dbg.traceback', False):
            import traceback
            traceback.print_exc()
        if settings.get('dbg.break_unknown_exception', False):
            import pdb
            pdb.set_trace()
        request.registry['logger'].log(str(e), type='error',
                                       severity=LOG.ERROR)
        raise http.HTTPServerError


@redir.get()
@redirl.get()
@checkService
def handle_redir(request):
    rlogger = request.registry.get('logger')
    storage = request.registry.get('storage')
    data = storage.resolve(request.matchdict.get('token'))
    if data is None:
        raise http.HTTPNotFound
    rlogger.log(type='redirect', severity=LOG.INFORMATIONAL,
                msg='redirect', fields=data)
    raise http.HTTPTemporaryRedirect(location=data['dest_url'])


@health.get()
def health_check(request):
    raise http.HTTPOk
