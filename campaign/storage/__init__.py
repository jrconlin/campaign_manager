# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#import memcache
from campaign.logger import LOG
from campaign.utils import as_id
from dateutil import parser
from inspect import stack
from sqlalchemy import (create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from time import time
import json
import math
import string

Base = declarative_base()


class StorageException(Exception):
    pass


class StorageBase(object):

    engine = None
    Session = None

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

    def _connect(self):
        try:
            if self.engine is None:
                userpass = ''
                host = ''
                if (self.settings.get('db.user')):
                    userpass = '%s:%s@' % (self.settings.get('db.user'),
                                           self.settings.get('db.password'))
                if (self.settings.get('db.host')):
                    host = '%s' % self.settings.get('db.host')
                dsn = '%s://%s%s/%s?charset=utf8' % (
                    self.settings.get('db.type', 'mysql'),
                    userpass, host,
                    self.settings.get('db.db',
                                      self.__database__))
                pool_size = int(self.settings.get('db.pool.size', '5'))
                max_overflow = int(self.settings.get('db.pool.max_overflow',
                                   '10'))
                recycle = int(self.settings.get('db.pool.recycle', '3600'))
                self.engine = create_engine(dsn,
                                            pool_size=pool_size,
                                            max_overflow=max_overflow,
                                            pool_recycle=recycle)
                Base.metadata.create_all(self.engine)
            if self.Session is None:
                self.Session = scoped_session(
                    sessionmaker(bind=self.engine,
                                 expire_on_commit=True))
        except Exception, e:
            self.logger.log(msg='Could not connect to db "%s"' % repr(e),
                            type='error', severity=LOG.EMERGENCY)
            raise e

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
        start_time = int(max(now, data.get('start_time', now)))
        end_time = start_time + (86400 * int(data.get('idle_time', 1)))
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
                    'text': data.get('body')
                }),
                'dest_url': data.get('dest_url'),
                'start_time': start_time,
                'end_time': end_time,
                'author': data.get('author'),
                'created': data.get('created', now),
                'specific': data.get('specific'),
                'title': data.get('ctitle'),
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
