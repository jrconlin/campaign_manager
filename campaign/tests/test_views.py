from campaign import views
from campaign.storage.sql import Storage
from campaign.tests import TConfig
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


class FakeMetlog():

    def metlog(self, **kw):
        self.lastRec = {'type': kw['type'],
                'payload': kw['payload'],
                'fields': kw['fields']}


class ViewTest(unittest2.TestCase):

    now = int(time.time())

    base_record = {
        'start_time': int(now),
        'end_time': int(now + 3000),
        'lang': 'en',
        'locale': 'US',
        'note': 'Body',
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
    ]

    def req(self, matchdict={}, user_id=None, headers=None, **kw):
        class Reg(dict):

            settings = {}

            def __init__(self, settings=None, **kw):
                super(Reg, self).__init__(**kw)
                if settings:
                    self.settings = settings
        request = Request(headers=headers, **kw)
        request.registry = Reg(settings=self.config.get_settings())
        request.registry['storage'] = self.storage
        request.registry['metlog'] = FakeMetlog()
        request.registry['auth'] = mock.Mock()
        request.registry['auth'].get_user_id.return_value = user_id
        if matchdict:
            request.matchdict.update(matchdict)
        return request

    def setUp(self):
        self.config = testing.setUp()
        self.storage = Storage(config=TConfig({'db.type': 'sqlite',
            'db.db': '/tmp/foo.db'}))
        for diff in self.diffs:
            record = self.base_record.copy()
            record.update(diff)
            self.storage.put_announce(record)

    def tearDown(self):
        self.storage.purge()

    def test_get_announcements(self):
        # normal number
        response = views.get_announcements(self.req(matchdict={'channel': 'a',
                'platform': 'a', 'version': 0}))
        eq_(len(response['announcements']), 3)
        # idle number
        response = views.get_announcements(self.req(matchdict={'channel': 'a',
                'platform': 'a', 'version': 0, 'idle_time': 6}))
        eq_(len(response['announcements']), 4)

    def test_get_all(self):
        self.assertRaises(http.HTTPUnauthorized,
                views.get_all_announcements,
                self.req())
        # scan for include.js or 'test="login"' id?
        # try with a 'valid' user id
        self.assertRaises(http.HTTPUnauthorized,
                views.get_all_announcements,
                self.req(matchdict={}, user_id='invalid@example.com'))
        # try successful json
        req = self.req(matchdict={}, user_id='foo@mozilla.com')
        req.accept_encoding = 'application/javascript'
        response = views.get_all_announcements(req)
        eq_(len(response['announcements']), 6)

    def test_handle_redir(self):
        # get a record
        response = self.storage.get_announce({'channel': 'b'})
        record = response[0]
        req = self.req(matchdict={'token': record['id']})
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
            'note': 'Ready for sacrifice'}, user_id='foo@mozilla.com')
        response = views.manage_announce(req)
        # test create
        time.sleep(2)  # Give the db a second to write the record.
        response = views.get_announcements(self.req(
            matchdict={'channel': 'c'}))
        goat = None
        for record in response['announcements']:
            if record['title'] == 'Goat':
                goat = record
                break
        self.assertIsNotNone(goat)
        req = self.req(params={'delete': goat['id']},
            user_id='foo@mozilla.com')
        self.assertRaises(http.HTTPOk, views.del_announce, req)
        time.sleep(2)  # Give the db a second to write the record.
        req = self.req(matchdict={'token': goat['id']})
        self.assertRaises(http.HTTPNotFound, views.handle_redir, req)
