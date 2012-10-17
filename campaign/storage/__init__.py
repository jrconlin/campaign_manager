# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#import memcache
from dateutil import parser
from time import time
import math
import json
import string

class StorageException(Exception):
    pass

class StorageBase(object):

    def __init__(self, config, **kw):
       self.config = config
       self.alphabet = string.digits + string.letters
       # self._mcache = memcache.Client(kw.get(servers,['localhost']))

    def _encode_num(self, num=0):
        if num == 0:
            return self.alphabet[0]
        barray = []
        base = len(self.alphabet)
        while num:
            remain = num % base
            num = num // base
            barray.append(self.alphabet[remain])
        barray.reverse
        return ''.join(barray)

    def _gen_key(self, data):
        """ Create a semi-arbitrary unique key for this record """
        nowbits = math.modf(time())
        return '%s%s' % (self._encode_num(int(nowbits[1])),
                self._encode_num(int(nowbits[0]*100000)))

    def parse_date(self, datestr):
        if not datestr:
            return None
        try:
            return float(datestr)
        except ValueError:
            pass
        try:
            return float (parser.parse(datestr).strftime('%s'))
        except ValueError:
            pass
        return None

    def normalize_announce(self, data):
        now = time()
        data['start_time'] = self.parse_date(data.get('start_time', now))
        data['end_time'] = self.parse_date(data.get('end_time'))
        for nullable in ('channel', 'platform', 'version'):
            if (data.get(nullable) in ('all','','0')):
                del data[nullable]
        snip = {
                'id': data.get('id'),
                'channel': data.get('channel'),
                'version': data.get('version'),
                'platform': data.get('platform'),
                'idle_time': data.get('idle_time', 0),
                'lang': data.get('lang'),
                'locale': data.get('locale'),
                'note': json.dumps({
                    'title': data.get('title'),
                    'text': data.get('note')
                    }),
                'dest_url': data.get('dest_url'),
                'start_time': data.get('start_time', now),
                'end_time': data.get('end_time'),
                'author': data.get('author'),
                'created': data.get('created', now),
                }
        if snip.get('id') is None:
            snip['id'] = self._gen_key(snip)
        return snip

    # customize for each memory model

    def del_announce(self, keys):
        pass

    def put_announce(self, data):
        data['id'] = self._gen_key(data)
        now = time()
        expry = None
        # auto expire if need be
        if data.get('end_time') and data.get('end_time') > now:
            expry = data.get('end_time') - now
        #self._mcache.add(key, value=data.get('note'),
        #   time=expry)

    def get_announce(self, data):
        key = self._gen_key(data)
        # if there are less entries in memcache than the total number of
        # possible iterations, just walk the list of items in memcache.

        # else build a set of test keys to see if anything matches
        # do a multi_get.

        # finally, if there isn't a minimum set of elements, fetch from the db.
