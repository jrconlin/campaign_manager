# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#import memcache
from dateutil import parser
from inspect import stack
from time import time
from campaign.utils import as_id
import math
import json
import string


class StorageException(Exception):
    pass


class StorageBase(object):

    def __init__(self, config, **kw):
        self.config = config
        self.settings = config.get_settings()
        self.alphabet = string.digits + string.letters
        self.memory = {}
        # self._mcache = memcache.Client(kw.get(servers,['localhost']))

    def _encode_num(self, num=0):
        return as_id(num)

    def _gen_key(self, data):
        """ Create a semi-arbitrary unique key for this record """
        nowbits = math.modf(time())
        return '%s%s' % (self._encode_num(int(nowbits[1])),
                self._encode_num(int(nowbits[0] * 100000)))

    def parse_date(self, datestr):
        if not datestr:
            return None
        try:
            return float(datestr)
        except ValueError:
            pass
        try:
            return float(parser.parse(datestr).strftime('%s'))
        except ValueError:
            pass
        return None

    def normalize_announce(self, data, now=None):
        if now is None:
            now = time()
        data['start_time'] = self.parse_date(data.get('start_time', now))
        data['end_time'] = self.parse_date(data.get('end_time'))
        for nullable in ('product', 'channel', 'platform', 'version', 'lang',
                         'locale'):
            if (data.get(nullable) in ('all', '', '0')):
                del data[nullable]
        snip = {'id': data.get('id'),
                'channel': data.get('channel'),
                'version': data.get('version'),
                'product': data.get('product'),
                'platform': data.get('platform'),
                'idle_time': data.get('idle_time', 0),
                'lang': data.get('lang'),
                'locale': data.get('locale'),
                'note': json.dumps({
                    'title': data.get('title'),
                    'text': data.get('note')
                }),
                'dest_url': data.get('dest_url'),
                'start_time': max(now, data.get('start_time', now)),
                'end_time': data.get('end_time'),
                'author': data.get('author'),
                'created': data.get('created', now),
                'specific': data.get('specific'),
                }
        if snip.get('id') is None:
            snip['id'] = self._gen_key(snip)
        return snip

    # customize for each memory model

    def health_check(self):
        """ Check that the current model is working correctly """
        # Is the current memory model working?
        return False

    def del_announce(self, keys):
        """ Delete the set of announcements. Called from UI. """
        raise StorageException('Undefined required method: ' %
                               stack()[0][3])

    def put_announce(self, data):
        """ Store the announcement (normalizing if necessary) """
        raise StorageException('Undefined required method: ' %
                               stack()[0][3])

    def get_announce(self, data):
        """ Retrieve matching announcements based on data """
        raise StorageException('Undefined required method: ' %
                               stack()[0][3])

    def get_all_announce(self, limit=None):
        """ Fetch all announcements (used by the UI) """
        raise StorageException('Undefined required method: ' %
                               stack()[0][3])

    def purge(self):
        """ Purge all listings (ONLY FOR TESTING) """
        raise StorageException('Undefined required method: ' %
                               stack()[0][3])
