#import memcache
from time import time
import math
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

    def refresh(self):
        # restock memcache from the db.
        pass


