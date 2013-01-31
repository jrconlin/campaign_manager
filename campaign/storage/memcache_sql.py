import logging
from campaign.storage.sql import Storage as SqlStorage
# Requires umemcache installed
from mozsvc.storage.mcclient import MemcachedClient


class Storage(SqlStorage):

    def __init__(self, config, **kw):
        try:
            super(Storage, self).__init__(config, **kw)
            self.memcache = MemcachedClient(
                servers=self.settings.get('db.memcache_servers'),
                key_prefix='cm_')
            self.expry = int(self.settings.get('db.query_window', 300))
        except Exception, e:
            logging.error('Could not initialize Storage "%s"', str(e))
            raise e

    def health_check(self):
        healthy = super(Storage, self).health_check()
        # TODO: MemCache health check
        return healthy

    def resolve(self, token):
        if token is None:
            return None
        record = self.memcache.get(token)
        if record is None:
            record = super(Storage, self).resolve(token)
        return record

    def _memcache_key(self, data):
        key = []
        fields = ['product', 'platform', 'channel', 'version', 'lang',
                  'locale', 'idle_time']
        # memcache keys are max 250 characters. max the string to the first
        # significant set of characters.
        maxLen = int(245 / len(fields)) - 1
        for field in fields:
            val = data.get(field) or 'NONE'
            key.append(val[:maxLen])
        return 'ca_' + '-'.join(key)

    def get_announce(self, data, now=None):
        mkey = self._memcache_key(data)
        record = self.memcache.get(mkey)
        if record is not None:
            if record == 0:
                return None
            return record
        else:
            record = super(Storage, self).get_announce(data, now)
            if record is None or len(record) == 0:
                record = 0
            self.memcache.set(mkey, record, self.expry)
            return record

    def del_announce(self, keys):
        for key in keys:
            self.memcache.delete(key)
        return super(Storage, self).del_announce(keys)
