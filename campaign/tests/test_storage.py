import time
import unittest2
from campaign.storage.sql import Storage

class TConfig:

    def __init__(self, data):
        self.settings = data

    def get_settings(self):
        return self.settings


class TestStorage(unittest2.TestCase):

    now = time.time()

    test_announce = {
            'start_time': now - 300,
            'end_time': now + 300,
            'idle_time': 0,
            'lang': 'en',
            'locale': 'US',
            'note': {'text': 'Text Body',
                     'title': 'Title'},
            'dest_url': 'http://example.com'
            }

    def setUp(self):
        import pdb; pdb.set_trace()
        self.storage = Storage(config = TConfig({'db.type': 'sqlite',
            'db.db': ':memory:'}))

    def test_put_announcement(self):
        import pdb; pdb.set_trace();
        self.storage.put_announce(self.test_announce)
        items = self.get_all_announce()
        self.failUnless(len(items) > 0)
        self.failUnless(self.test_announce['note']['text'] in items[0].note)
        self.failUnless(self.test_announce['note']['title'] in items[0].note)
        self.failUnless(self.test_announce['dest_url'] in items[0].dest_url)

#TODO: continue tests
