from campaign import views
from campaign.storage.sql import Storage
from campaign.tests import TConfig
from campaign.logger import Logging
from nose.tools import eq_
from pyramid import testing
import json
import mock
import pyramid.httpexceptions as http
import time
import unittest2


def Request(params=None, post=None, matchdict=None, headers=None,
            registry=None, **kw):

    class Errors(list):
        def add(self, where, key, msg):
            self.append((where, key, msg))

    testing.DummyRequest.json_body = property(lambda s: json.loads(s.body))
    request = testing.DummyRequest(params=params, post=post, headers=headers,
                                   **kw)
    request.route_url = lambda s, **kw: s.format(**kw)
    if matchdict:
        request.matchdict = matchdict
    if registry:
        request.registry.update(registry)
    return request


class ViewTest(unittest2.TestCase):

    now = 10000

    base_record = {
        'start_time': int(now),
        'end_time': int(now + 3000),
        'lang': 'en',
        'locale': 'US',
        'body': 'Body',
        'title': 'Title',
        'dest_url': 'http://example.com'
    }

    diffs = [
        {'channel': None, 'platform': None, 'version': None, 'title': 'all'},
        {'channel': 'a', 'platform': None, 'version': None, 'title': 'ann'},
        {'channel': 'a', 'platform': 'a', 'version': 0, 'title': 'aa0'},
        {'channel': 'a', 'platform': 'a', 'version': 0, 'idle_time': 1,
            'title': 'aa0i1'},
        {'channel': 'a', 'platform': 'b', 'version': 0, 'title': 'ab0'},
        {'channel': 'b', 'platform': 'a', 'version': 2, 'title': 'ba2',
            'dest_url': 'http://example.org'},
        {'channel': 'e', 'platform': None, 'version': None,
            'title': 'utf8',
            'body':  "\u0192\u00a9\u02d9\u02da\u02da\u00ac\u2206\u02d9\u02da\u02d9\u00a9\u2206\u00a9\u0192\u00df \u0376\u0376\u0376\u0376\u0376\u0376\u0376\u0376\u0376\u0376\u0376\u0376\u0376\u0376"}
    ]

    def req(self, matchdict={}, user_id=None, headers=None, **kw):

        class Reg(dict):

            settings = {}

            def __init__(self, settings=None, **kw):
                super(Reg, self).__init__(**kw)
                if settings:
                    self.settings = settings

        request = Request(headers=headers, **kw)
        request.GET = kw.get('params',{})
        request.registry = Reg(settings=self.config.get_settings())
        request.registry['storage'] = self.storage
        request.registry['logger'] = self.logger
        request.registry['auth'] = mock.Mock()
        request.registry['auth'].get_user_id.return_value = user_id
        if matchdict:
            request.matchdict.update(matchdict)
        return request

    def setUp(self):
        self.config = testing.setUp()
        tsettings = TConfig({'db.type': 'sqlite',
                             'db.db': '/tmp/test.db',
                             'logging.use_metlog': False})
        self.storage = Storage(config=tsettings)
        self.logger = Logging(tsettings, None)
        records = []
        for diff in self.diffs:
            record = self.base_record.copy()
            record.update(diff)
            records.append(record)
        self.storage.put_announce(records, now=self.now)
        #time.sleep(3);

    def tearDown(self):
        self.storage.purge()

    def test_get_announcements(self):
        # normal number
        response = views.get_announcements(self.req(matchdict={'channel': 'a',
                                           'platform': 'a', 'version': 0}),
                                           now=self.now)
        eq_(len(json.loads(response.body)['announcements']), 3)
        assert('Date' in response.headers)
        response = views.get_announcements(self.req(matchdict={'channel': 'a',
                                           'platform': 'a', 'version': 0},
                                           headers={'Accept-Language': 'en'}),
                                           now=self.now)
        eq_(len(json.loads(response.body)['announcements']), 3)
        # idle number
        response = views.get_announcements(self.req(matchdict={'channel': 'a',
                              'platform': 'a',
                              'version': 0},
                              params={'idle': '6'}))
        eq_(len(json.loads(response.body)['announcements']), 4)
        timestamp = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                                  time.gmtime(self.now + 1))
        self.assertRaises(http.HTTPNotModified,
                          views.get_announcements,
                          self.req(matchdict={'channel': 'a',
                                              'platform': 'a', 'version': 0},
                          headers={'If-Modified-Since': timestamp}))
        self.storage.purge()
        self.assertRaises(http.HTTPNoContent,
                          views.get_announcements,
                          self.req(matchdict={'channel': 'z', 'platform': 'z',
                                              'version': 'z'}))

    def test_get_all(self):
        self.assertRaises(http.HTTPUnauthorized,
                          views.get_all_announcements,
                          self.req())
        # scan for include.js or 'test="login"' id?
        # try with a 'valid' user id
        self.assertRaises(http.HTTPUnauthorized,
                          views.get_all_announcements,
                          self.req(matchdict={},
                                   user_id='invalid@example.com'))
        # try successful json
        req = self.req(matchdict={}, user_id='foo@mozilla.com')
        req.accept_encoding = 'application/javascript'
        response = views.get_all_announcements(req)
        eq_(len(response['announcements']), 7)

    def test_get_lang_loc(self):
        response = views.get_lang_loc(self.req(
                                      headers={'Accept-Language': 'en_US'}))
        eq_(response, {'lang': 'en', 'locale': 'US'})
        response = views.get_lang_loc(self.req(
                                      headers={'Accept-Language': 'en-US'}))
        eq_(response, {'lang': 'en', 'locale': 'US'})
        response = views.get_lang_loc(self.req(
                                      headers={'Accept-Language': 'en'}))
        eq_(response, {'lang': 'en', 'locale': None})

    def test_handle_redir(self):
        # get a record
        response = self.storage.get_announce({'channel': 'b'})
        record = response[0]
        rec_id = record['url'].split('/').pop()
        req = self.req(matchdict={'token': rec_id})
        self.assertRaises(http.HTTPTemporaryRedirect,
                          views.handle_redir, req)
        self.assertRaises(http.HTTPNotFound, views.handle_redir,
                          self.req(matchdict={'token': 'Invalid Token'}))

    def test_admin_page(self):
        req = self.req()
        response = views.admin_page(req)
        eq_(response.status_code, 403)
        req = self.req(matchdict={}, user_id='foo@mozilla.com')
        response = views.admin_page(req)
        eq_(response.status_code, 200)
        req.registry.settings.update({'auth.block_authoring': True})
        self.assertRaises(http.HTTPNotFound, views.admin_page, req)

    def test_manage_announce(self):
        # test assertion post
        req = self.req(matchdict={'channel': 'c', 'title': 'Goat',
                                  'body': 'Ready for sacrifice'},
                       user_id='foo@mozilla.com')
        response = views.manage_announce(req)
        # test create
        ann = views.get_announcements(self.req(matchdict={'channel': 'c'}))
        response = json.loads(ann.body)
        goat = None
        for record in response['announcements']:
            if record['title'] == 'Goat':
                goat = record
                break
        goat_id = goat['url'].split('/').pop()
        self.assertIsNotNone(goat)
        req = self.req(params={'delete': goat_id},
                       user_id='foo@mozilla.com')
        self.assertRaises(http.HTTPOk, views.del_announce, req)
        time.sleep(2)  # Give the db a second to write the record.
        req = self.req(matchdict={'token': goat_id})
        self.assertRaises(http.HTTPNotFound, views.handle_redir, req)
