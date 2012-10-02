#import memcache
from time import time


class StorageBase(object):

    def __init__(self, config, **kw):
       self.config = config
       # self._mcache = memcache.Client(kw.get(servers,['localhost']))

    def _gen_key(self, **kw):
        key = ''
        for k in ['idle_time', 'lang', 'locale', 'client', 'platform']:
            key +='%s=%s|' % (k, kw.get(k, ''))
        return key

    def put(self, **data):
        key = self._gen_key(**data)
        now = time()
        expry = None
        # auto expire if need be
        if data.get('end_time') and data.get('end_time') > now:
            expry = data.get('end_time') - now
        #self._mcache.add(key, value=data.get('note'),
        #   time=expry)

    def get(self, **data):
        key = self._gen_key(**data)
        # if there are less entries in memcache than the total number of
        # possible iterations, just walk the list of items in memcache.

        # else build a set of test keys to see if anything matches
        # do a multi_get.

        # finally, if there isn't a minimum set of elements, fetch from the db.

    def refresh(self):
        # restock memcache from the db.
        pass
