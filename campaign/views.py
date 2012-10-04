""" Cornice services.
"""
from . import LOG
from mozsvc.metrics import Service
from mako.template import Template
from pyramid.httpexceptions import (HTTPNotModified, HTTPNoContent,
        HTTPNotFound, HTTPServerError)
from time import strptime
from webob import Response
import json
import os


fetch = Service(name='fetch',
        path='/campaigns/{channel}/{version}/{platform}',
        description='Fetcher')
author = Service(name='author',
        path='/author/',
        description='Authoring Interface')
fstatic = Service(name='fstatic',
        path='/{file}',
        description='hack')

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
    for item in reply['snippets']:
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
    reply = storage.get(**args)
    metlog.metlog(type='campaign', payload='fetch', fields=args)
    if not len(reply):
        if last_accessed:
            raise HTTPNotModified
        else:
            raise HTTPNoContent
    log_fetched(reply)
    return reply

def user_authed(request):
    # TODO: set as decorator?
    # TODO: limit to mozilla IPs?
    # is the user logged in?
    # is the bid from mozilla?
    pass

def get_template(name):
    name = os.path.join(_TMPL, '%s.mako' % name)
    try:
        return Template(filename=name)
    except IOError:
        raise HTTPServerError


def get_file(name):
    try:
        name = os.path.join(_TMPL, '%s' % name)
        ff = open(name)
        return ff.read()
    except IOError:
        raise HTTPNotFound


def get_ideltime(request):
    return {'idle_time': int(request.params.get('idle', 0))}


@author.get()
def get_author(request):
    #if authorized:
    # get list of promos
    #metlog = request.registry.get('metlog')
    storage = request.registry.get('storage')
    tdata = {}
    tdata['notes'] = storage.get_all(limit=10)
    template = get_template('main')
    content_type = 'text/html'
    reply = template.render(**tdata)
    response = Response(str(reply), content_type=content_type)
    return response

@author.post()
def put_author(request):
    storage = request.registry.get('storage')
    import pdb; pdb.set_trace();
    storage.put(request.matchdict)

@fstatic.get()
def get_static(request):
    response = Response(str(get_file(request.matchdict.get('file'))),
            content_type = 'text/css')
    return response
