# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
""" Cornice services.
"""
from campaign import logger, LOG
from campaign.auth.default import DefaultAuth
from mozsvc.metrics import Service
from mako.template import Template
import pyramid.httpexceptions as http
from time import strptime
from webob import Response
import json
import os


fetch = Service(name='fetch',
        path='/announcements/{channel}/{platform}/{version}',
        description='Fetcher')
get_all = Service(name="get_all",
        path='/announcements/',
        description='Fetch Everything')
author2 = Service(name='author2',
        path='/author/{id}',
        description='Authoring Interface with record')
author = Service(name='author',
        path='/author/',
        description='Authoring Interface')
fstatic = Service(name='fstatic',
        path='/{file}',
        description='hack')
logout = Service(name='logout',
        path='/logout/',
        description='logout')
redirl = Service(name='redir2',
        path='/redirect/{locale}/{token}',
        description='redir with locale')
redir = Service(name='redir',
        path='/redirect/{token}',
        description='redir')
root = Service(name='root',
        path='/',
        description='Default path')


_TMPL = os.path.join(os.path.dirname(__file__), 'templates')


def get_lang_loc(request):
    header = request.headers.get('Accept-Language', 'en-US')
    langloc = header.split(',')[0]
    if ('-' in langloc):
        (lang, loc) = langloc.split('-')
    else:
        (lang, loc) = (langloc, None)
    return {'lang': lang.lower(), 'locale': loc.upper()}


def get_last_accessed(request):
    last_accessed = None
    try:
        if 'If-Modified-Since' in request.headers:
            last_accessed_str = request.headers.get('If-Modified-Since')
            last_accessed = strptime(last_accessed_str)
    except Exception, e:
        settings = request.registry.settings
        if settings.get('dbg.traceback', False):
            import traceback
            traceback.print_exc()
        if settings.get('dbg.break_unknown_exception', False):
            import pdb
            pdb.set_trace()
        request.registry['metlog'].metlog(type='campaign_error',
                severity=LOG.ERROR,
                payload='Exception: %s' % str(e))
    return {'last_accessed': last_accessed}


def log_fetched(request, reply):
    metlog  = request.registry['metlog'].metlog
    for item in reply['announcements']:
        metlog(type='campaign_log',
                severity=LOG.NOTICE,
                payload='fetched',
                fields=json.dumps(item))
        pass

@fetch.get()
def get_snippets(request):
    """Returns campaigns in JSON."""
    # get the valid user information from the request.
    metlog = request.registry.get('metlog')
    storage = request.registry.get('storage')
    args = request.matchdict
    args.update(get_lang_loc(request))
    last_accessed = get_last_accessed(request)
    args.update(last_accessed)
    reply = {'announcements': storage.get_announce(args)}
    metlog.metlog(type='campaign', payload='fetch_query', fields=args)
    if not len(reply):
        if last_accessed:
            raise http.HTTPNotModified
        else:
            raise http.HTTPNoContent
    log_fetched(request, reply)
    return reply


def get_template(name):
    name = os.path.join(_TMPL, '%s.mako' % name)
    try:
        return Template(filename=name)
    except IOError, e:
        logger.error(str(e))
        raise http.HTTPServerError


def get_file(name):
    try:
        name = os.path.join(_TMPL, '%s' % name)
        ff = open(name)
        return ff.read()
    except IOError:
        raise http.HTTPNotFound


def authorized(email, request):
    if email is None:
        return False
    settings = request.registry.settings
    try:
        domains = json.loads(settings.get('auth.valid.domains',
            '["@mozilla.com", "@mozilla.org"]'))
        for valid_domain in domains:
            if email.lower().endswith(valid_domain):
                return True
    except TypeError, e:
        pass
    except Exception, e:
        if settings.get('dbg.traceback', False):
            import traceback
            traceback.print_exc()
        if settings.get('dbg.break_unknown_exception', False):
            import pdb
            pdb.set_trace()
        pass
    return False


@get_all.get()
def get_all_snippets(request):
    if not login(request):
        raise http.HTTPUnauthorized;
    storage = request.registry.get('storage')
    tdata = {"announcements": storage.get_all_announce()}
    return tdata


@author.get()
@author2.get()
def admin_page(request, error=None):
    if request.registry.settings.get('auth.block_authoring', False):
        raise http.HTTPNotFound()
    if not login(request):
        return login_page(request)
    tdata = get_all_snippets(request)
    tdata['author'] = request.session['uid']
    tdata['error'] = error
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
    response = Response(str(reply), content_type=content_type)
    return response


# sad to use post for DELETE, but JQuery doesn't add args to DELETE for bulk.
@author.post()
@author2.post()
def manage_announce(request):
    args = request.params.copy()
    if request.registry.settings.get('auth.block_authoring', False):
        raise http.HTTPNotFound()
    if not login(request):
        return http.HTTPUnauthorized
    else:
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
        if args != None and len(args) > 0:
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
    return admin_page(request, err);

@author.delete()
def del_announce(request):
    if not login(request):
        return login_page(request)
    storage = request.registry.get('storage')
    args = dict(request.params)
    deleteables = args.get('delete', args.get('delete[]', '')).split(',')
    if len(deleteables):
        storage.del_announce(deleteables)
    raise http.HTTPOk


@fstatic.get()
def get_static(request):
    response = Response(str(get_file(request.matchdict.get('file'))),
            content_type = 'text/css')
    return response

@root.get()
def boot_to_author(request):
    return http.HTTPTemporaryRedirect(location='/author/')

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
    login_page(request)


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
        response = Response(str(template.render(
            audience=request.get('HTTP_HOST'))),
            status=403)
        if (session.get('uid')):
            del(session['uid'])
        try:
            session.persist()
            session.save()
        except AttributeError:
            pass # because testing
        return response
    except Exception, e:
        settings = request.registry.settings
        if settings.get('dbg.traceback', False):
            import traceback
            traceback.print_exc()
        if settings.get('dbg.break_unknown_exception', False):
            import pdb
            pdb.set_trace()
        logger.error(str(e))
        raise http.HTTPServerError

def login(request, skipAuth=False):
    params = dict(request.params.items())
    try:
        if (request.json_body):
            params.update(request.json_body.items())
    except ValueError:
        pass
    try:
        uid = request.session.get('uid')
        if uid and authorized(uid, request):
            return True;
        #config = request.registry.get('config', {})
        auth = request.registry.get('auth', DefaultAuth)
        email = auth.get_user_id(request)
        if email is None:
            return False
        if authorized(email, request):
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
        if settings.get('dbg.traceback', False):
            import traceback
            traceback.print_exc()
        if settings.get('dbg.break_unknown_exception', False):
            import pdb
            pdb.set_trace()
        logger.error(str(e))
        return False
    # User Logged in
    return True

@redir.get()
@redirl.get()
def handle_redir(request):
    metlog = request.registry.get('metlog')
    storage = request.registry.get('storage')
    data = storage.resolve(request.matchdict.get('token'));
    if data is None:
        raise http.HTTPNotFound
    metlog.metlog(type='campaign', payload='redirect', fields=data)
    raise http.HTTPTemporaryRedirect(location=data['dest_url'])
