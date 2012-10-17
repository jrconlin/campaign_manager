# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
""" Cornice services.
"""
from campaign import LOG
from campaign.auth.default import DefaultAuth
from mozsvc.metrics import Service
from mako.template import Template
import pyramid.httpexceptions as err
from time import strptime
from webob import Response
import json
import os


fetch = Service(name='fetch',
        path='/announcements/{channel}/{platform}/{version}',
        description='Fetcher')
fetchall = Service(name="fetchall",
        path='/announcements/',
        description='Fetch Everything')
authorx = Service(name='authorx',
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
redir = Service(name='redir',
        path='/redirect/{token}',
        description='redir')


_TMPL = os.path.join(os.path.dirname(__file__), 'templates')


def get_lang_loc(request):
    header = request.headers.get('Accept-Language', 'en-us')
    langloc = header.split(',')[0]
    if ('-' in langloc):
        (lang, loc) = langloc.split('-')
    else:
        (lang, loc) = (langloc, None)
    return {'lang': lang, 'locale': loc}


def get_last_accessed(request):
    last_accessed = None
    try:
        if 'If-Modified-Since' in request.headers:
            last_accessed_str = request.headers.get('If-Modified-Since')
            last_accessed = strptime(last_accessed_str)
    except Exception, e:
        import pdb; pdb.set_trace()
        request.registry['metlog'].metlog(type='campaign_error',
                severity=LOG.ERROR,
                payload='Exception: %s' % str(e))
    return {'last_accessed': last_accessed}


def log_fetched(request, reply):
    logger = request.registry['metlog'].metlog
    for item in reply['announcements']:
        continue; ## NOOP
        logger(type='campaign_log',
                severity=LOG.INFO,
                payload=json.dumps(item))
        #metlogger.metlog('msgtype', payload='payload')
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
    metlog.metlog(type='campaign', payload='fetch', fields=args)
    if not len(reply):
        if last_accessed:
            raise err.HTTPNotModified
        else:
            raise err.HTTPNoContent
    log_fetched(request, reply)
    return reply


def get_template(name):
    name = os.path.join(_TMPL, '%s.mako' % name)
    try:
        return Template(filename=name)
    except IOError:
        raise err.HTTPServerError


def get_file(name):
    try:
        name = os.path.join(_TMPL, '%s' % name)
        ff = open(name)
        return ff.read()
    except IOError:
        raise err.HTTPNotFound


def get_ideltime(request):
    return {'idle_time': int(request.params.get('idle', 0))}


def authorized(request, email):
    if email is None:
        return False
    settings = request.registry.settings
    try:
        domains = json.loads(settings.get('auth.valid.domains',
            "['@mozilla.com', '@mozilla.org']"))
        for valid_domain in domains:
            if email.lower().endswith(valid_domain):
                return True
    except TypeError, e:
        pass
    except Exception, e:
        import pdb; pdb.set_trace();
        pass
    return False


@fetchall.get()
def fetchall_snippets(request):
    if not authorized(request, request.session.get('uid')):
        return login(request)
    storage = request.registry.get('storage')
    tdata = {"notes": storage.get_all_announce()}
    return tdata


@author.get()
@authorx.get()
def admin_page(request, error=None):
    if not authorized(request, request.session.get('uid')):
        return login(request)
    tdata = fetchall_snippets(request)
    tdata['author'] = request.session['uid']
    tdata['error'] = error
    template = get_template('main')
    content_type = 'text/html'
    reply = template.render(**tdata)
    response = Response(str(reply), content_type=content_type)
    return response


# sad to use post for DELETE, but JQuery doesn't add args to DELETE for bulk.
@author.post()
@authorx.post()
def manage_announce(request):
    if not authorized(request, request.session.get('uid')):
        return login(request)
    storage = request.registry.get('storage')
    session = request.session
    args = dict(request.params)
    err = None
    if not args.get('author'):
        args['author'] = session.get('uid')
    if 'assertion' in args:
        """ Login request"""
        return admin_page(request)
    if 'delete' in args or 'delete[]' in args:
        try:
            del_announce(request)
        except err.HTTPOk:
            pass
        except err.HTTPNotFound, e:
            import pdb; pdb.set_trace();
            pass
        return admin_page(request)
    if not args.get('author'):
        args['author'] = session.get('uid')
    try:
        storage.put_announce(args)
    except Exception, e:
        import pdb; pdb.set_trace()
        # display error page.
        pass
    return admin_page(request);

@author.delete()
def del_announce(request):
    if not authorized(request, request.session.get('uid')):
        return login(request)
    storage = request.registry.get('storage')
    args = dict(request.params)
    deleteables = args.get('delete', args.get('delete[]', '')).split(',')
    if len(deleteables):
        storage.del_announce(deleteables)
    raise err.HTTPOk


@fstatic.get()
def get_static(request):
    response = Response(str(get_file(request.matchdict.get('file'))),
            content_type = 'text/css')
    return response

@logout.delete()
def logout_page(request):
    session = request.session
    if 'uid' in session:
        del session['uid']
        session.persist()
        session.save()
    login_page(request)


def login_page(request):
    session = request.session
    template = get_template('login')
    response = Response(str(template.render(audience=request.get('HTTP_HOST'))),
        status=403)
    if (session.get('uid')):
        del(session['uid'])
    session.persist()
    session.save()
    return response

def login(request, skipAuth=False):
    params = dict(request.params.items())
    try:
        if (request.json_body):
            params.update(request.json_body.items())
    except ValueError:
        pass
    try:
        #config = request.registry.get('config', {})
        auth = request.registry.get('auth', DefaultAuth)
        email = auth.get_user_id(request)
        if email is None:
            return login_page(request)
        if authorized(request, email):
            session = request.session
            session['uid'] = email
            session.persist()
            session.save()
        else:
            return login_page(request)
    except Exception, e:
        import pdb; pdb.set_trace();
        print ('missing credentials? %s', str(e))
        return login_page(request)
    # User Logged in
    return manage_announce(request)

@redir.get()
def handle_redir(request):
    metlog = request.registry.get('metlog')
    storage = request.registry.get('storage')
    data = storage.resolve(request.matchdict.get('token'));
    if data is None:
        return err.HTTPNotFound
    metlog.metlog(type='campaign', payload='redirect', fields=data)
    return err.HTTPTemporaryRedirect(location=data['dest_url'])
