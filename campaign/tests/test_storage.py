from campaign.storage.sql import Storage
from campaign.logger import Logging
from campaign.tests import TConfig
import json
import unittest2


class TestStorage(unittest2.TestCase):

    now = 10000

    test_announce = {
        'start_time': int(now - 300),
        'end_time': int(now + 3000),
        'lang': 'en',
        'locale': 'US',
        'body': 'Text Body',
        'title': 'Test',
        'dest_url': 'http://example.com'
    }

    config = TConfig({'db.type': 'sqlite',
                      'db.db': '/tmp/test.db',
                      'logging.use_heka': False})
    logger = Logging(config, None)

    def setUp(self):
        self.storage = Storage(config=self.config, logger=self.logger)

    def tearDown(self):
        self.storage.purge()
        del self.storage

    def test_health_check(self):
        result = self.storage.health_check()
        self.assertEquals(result, True)

    def test_announcement(self):
        self.storage.put_announce(self.test_announce, now=self.now)
        items = self.storage.get_all_announce()
        self.failUnless(len(items) > 0)
        self.failUnless('text' in items[0]['note'])
        self.failUnless('title' in items[0]['note'])
        self.failUnless(self.test_announce['body'] in items[0]['note'])
        self.failUnless(self.test_announce['title'] in items[0]['note'])
        self.failUnless(self.test_announce['dest_url'] in items[0]['dest_url'])

    def update_note(self, announce, note_text):
        return announce.copy()

    def reload(self):
        records = []
        updates = [{'lang': None, 'locale': None, 'title': 'Everyone'},
                   {'platform': 'a', 'channel': 'a', 'title': 'p:a;c:a'},
                   {'platform': 'b', 'channel': 'a', 'title': 'p:b;c:a'},
                   {'platform': 'a', 'start_time': self.now + 20,
                    'end_time': self.now + 3000, 'title': 'notyet'},
                   #{'platform': 'a', 'end_time': self.now - 50,
                   # 'title': 'tooold'},
                   {'platform': 'a', 'idle_time': 10, 'title': 'idle: 10'},
                   {'platform': 'a', 'channel': 'b', 'lang': 'a',
                    'locale': 'a', 'idle_time': 10, 'title': 'full_rec'}]
        # load the database
        for update in updates:
            test = self.test_announce.copy()
            test.update(update)
            records.append(test)
        self.storage.put_announce(records, now=self.now)
        #time.sleep(3);

    def test_search0(self):
        """ Yes, this test does a lot of things. That's because I need
        to exercise the search algo using a lot of records. """
        # really wish that update allowed chaining.
        self.reload()
        data = {'platform': 'f', 'channel': 'f', 'version': 0}
        announce = self.storage.get_announce(data, now=self.now + 86400 * 2)
        self.assertEqual(len(announce), 1)
        self.assertEqual(announce[0]['title'], 'Everyone')

    def test_search1(self):
        self.reload()
        data = {'platform': 'a', 'channel': 'a'}
        print "P&C check:"
        announce = self.storage.get_announce(data, now=self.now + 10)
        # only Everyone and p: a;c: a should be returned.
        self.assertEqual(len(announce), 2)
        # Make sure the most specific entry is returned first.
        self.assertEqual(announce[0].get('title'), 'p:a;c:a')

    def test_search2(self):
        self.reload()
        data = {'platform': 'a', 'channel': 'a', 'idle': 15}
        print "Idle Check:"
        announce = self.storage.get_announce(data, now=self.now)
        self.assertEqual(len(announce), 3)

    def test_search3(self):
        self.reload()
        data = {'platform': 'a', 'channel': 'b'}
        announce = self.storage.get_announce(data, now=self.now + 10)
        print "P&C2 check:"
        self.assertEqual(len(announce), 1)
        # Store the unique record data for the resolve check.
        resolve_rec = announce[0]
        goat_id = resolve_rec['url'].split('/').pop()

        data = {'platform': 'a', 'channel': 'a'}
        print self.now + 21
        print "Wake check: %s " % (self.now + 21)
        announce = self.storage.get_announce(data, now=self.now + 21)
        self.assertEqual(len(announce), 3)

        # Since we have an ID for a unique record, query it to make
        # sure records resolve.
        print "resolve check: %s" % goat_id
        rec = self.storage.resolve(goat_id)
        self.assertEqual('Everyone', json.loads(rec['note'])['title'])

#TODO: continue tests
