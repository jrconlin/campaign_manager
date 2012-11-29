import logging
import json
import time
from . import StorageException
from .sql import Storage as SqlStorage
# Requires umemcache installed
from mozsvc.storage.mcclient import MemcachedClient


class Storage(SqlStorage):

    def __init__(self, config, **kw):
        try:
            super(SqlStorage, self).__init__(config, kw)
            self.memcache = MemcachedClient(
                servers=config.get('storage.memcache_servers'),
                key_prefix='cm_')

        except Exception, e:
            import pdb; pdb.set_trace();
            logging.error('Could not initialize Storage "%s"', str(e))
            raise e

    def health_check(self):
        healthy = super(SqlStorage, self).health_check()
        #TODO: check memcache health

        return healthy

    def resolve(self, token):
        if token is None:
            return None
        record = self.memcache.get(token)
        if record is None:
            record = super(SqlStorage, self).resolve(token)
        return record

    def _memcache_key(self, data):

    def get_announce(self, data):
        
