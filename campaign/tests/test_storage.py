from campaign.storage.sql import Storage
from campaign.tests import TConfig
import json
import time
import unittest2


class TestStorage(unittest2.TestCase):

    now = int(time.time())

    test_announce = {
        'start_time': int(now - 300),
        'end_time': int(now + 3000),
        'lang': 'en',
        'locale': 'US',
        'note': 'Text Body',
        'title': 'Test',
        'dest_url': 'http://example.com'
    }

    def setUp(self):
        self.storage = Storage(config=TConfig({'db.type': 'sqlite',
            'db.db': ':memory:'}))

    def tearDown(self):
        self.storage.purge()

    def test_health_check(self):
        result = self.storage.health_check()
        self.assertEquals(result, True)

    def test_announcement(self):
        self.storage.put_announce(self.test_announce)
        items = self.storage.get_all_announce()
        self.failUnless(len(items) > 0)
        self.failUnless(self.test_announce['note'] in items[0].note)
        self.failUnless(self.test_announce['title'] in items[0].note)
        self.failUnless(self.test_announce['dest_url'] in items[0].dest_url)

    def update_note(self, announce, note_text):
        return announce.copy()

    def test_search(self):
        """ Yes, this test does a lot of things. That's because I need
        to exercise the search algo using a lot of records. """
        # really wish that update allowed chaining.
        updates = [{'lang': None, 'locale': None, 'title': 'Everyone'},
            {'platform': 'a', 'channel': 'a', 'title': 'p:a;c:a'},
            {'platform': 'b', 'channel': 'a', 'title': 'p:b;c:a'},
            {'platform': 'a', 'start_time': self.now + 1,
                'end_time': self.now + 3, 'title': 'notyet'},
            {'platform': 'a', 'end_time': self.now - 5, 'title': 'tooold'},
            {'platform': 'a', 'idle_time': 10, 'title': 'idle: 10'},
            {'platform': 'a', 'channel': 'b', 'lang': 'a', 'locale': 'a',
                'idle_time': 10, 'title': 'full_rec'}
        ]
        # load the database
        for update in updates:
            test = self.test_announce.copy()
            test.update(update)
            self.storage.put_announce(test)
        data = {'platform': 'f', 'channel': 'f', 'version': 0}
        announce = self.storage.get_announce(data)
        self.assertEqual(len(announce), 1)
        self.assertEqual(announce[0]['title'], 'Everyone')
        data = {'platform': 'a', 'channel': 'a'}
        announce = self.storage.get_announce(data)
        # only Everyone and p: a;c: a should be returned.
        print "P&C check:"
        self.assertEqual(len(announce), 2)
        # Make sure the most specific entry is returned first.
        self.assertEqual(announce[0].get('title'), 'p:a;c:a')

        data = {'platform': 'a', 'channel': 'a', 'idle_time': 15}
        announce = self.storage.get_announce(data)
        print "Idle Check:"
        self.assertEqual(len(announce), 3)

        data = {'platform': 'a', 'channel': 'b'}
        announce = self.storage.get_announce(data)
        print "P&C2 check:"
        self.assertEqual(len(announce), 1)
        # Store the unique record data for the resolve check.
        resolve_rec = announce[0]

        data = {'platform': 'a', 'channel': 'a'}
        time.sleep(self.now + 2 - int(time.time()))
        print "Wake check: %s " % (int(time.time()) - self.now)
        announce = self.storage.get_announce(data)
        self.assertEqual(len(announce), 3)

        time.sleep(self.now + 4 - int(time.time()))
        print "Expire check: %s " % (int(time.time()) - self.now)
        data = {'platform': 'a', 'channel': 'a'}
        announce = self.storage.get_announce(data)
        self.assertEqual(len(announce), 2)

        # Since we have an ID for a unique record, query it to make
        # sure records resolve.
        print "resolve check: %s" % resolve_rec['id']
        rec = self.storage.resolve(resolve_rec['id'])
        self.assertEqual('Everyone', json.loads(rec['note'])['title'])

#TODO: continue tests
