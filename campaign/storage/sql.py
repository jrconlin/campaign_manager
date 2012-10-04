import logging
import json
from time import time
from sqlalchemy import (Table, Column, Integer, String, Text, Float,
        create_engine, MetaData, text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from campaign.storage import StorageBase

Base = declarative_base()
Session = scoped_session(sessionmaker())

class Storage(StorageBase):
    __database__ = 'campaign'
    __tablename__ = 'campaigns'

    def __init__(self, config, **kw):
        try:
            super(Storage, self).__init__(config, **kw)
            self.metadata = MetaData()
            self.campaigns = Table(self.__tablename__, self.metadata,
                Column('id', String(25), primary_key=True),
                Column('channel', String(24), index=True, nullable=True),
                Column('version', Float, index=True, nullable=True),
                Column('platform', String(24), index=True, nullable=True),
                Column('lang', String(24), index=True),
                Column('locale', String(24), index=True, nullable=True),
                Column('start_time', Integer, index=True),
                Column('end_time', Integer, index=True, nullable=True),
                Column('idle_time', Integer, index=True, nullable=True),
                Column('note', Text),
                Column('author', String(255), index=True),
                Column('created', Integer, index=True))
            self._connect()
            #TODO: add the most common index.
        except Exception, e:
            logging.error('Could not initialize Storage "%s"', str(e))
            raise e

    def _connect(self):
        try:
            settings = self.config.get_settings()
            dsn = 'mysql://%s:%s@%s/%s' % (
                    settings.get('mysql.user', 'user'),
                    settings.get('mysql.password', 'password'),
                    settings.get('mysql.host', 'localhost'),
                    settings.get('msyql.db', self.__database__))
            self.engine = create_engine(dsn, pool_recycle=3600)
            self.metadata.create_all(self.engine)
        except Exception, e:
            logging.error('Could not connect to db "%s"' % repr(e))
            raise e



    def put(self, note, author, created,
            version=None, channel=None, platform=None,
            lang='en', locale='us',
            idle_time=0, start_time=None, end_time=None):
        now = time()
        snip = {
                'channel': channel,
                'version': version,
                'platform': platform,
                'idle': idle_time,
                'lang': lang,
                'locale': locale,
                'note': note,
                'start_time': start_time if start_time else now,
                'end_time': end_time,
                'author': author,
                'created': created if created else now,
                }
        self.insert(snip)
        query = ("insert into %s.%s " % (self.__database__,
                    self.__tablename__) +
                "(start_time, end_time, idle_time, "
                "lang, locale, channel, platform, version, "
                "created, author, note) "
                "values (:start_time, :end_time, :idle_time, "
                ":lang, :locale, :channel, :platform, :version, "
                ":created, :author, :note);")
        self.engine.execute(text(query), **dict(snip))
        return self

    def get(self, channel=None, platform=None, version=None,
            lang='en', locale=None,
            start_time=None, end_time=None, author=None, created=None,
            idle_time=0, last_accessed=None, **kw):
        # Really shouldn't allow "global" variables, but I know full well
        # that they're going to want them.
        params = {}
        sql =("select id, note from %s.%s where " % (self.__database__,
                self.__tablename__) +
            " start_time < unix_timestamp() and end_time > unix_timestamp() ")
        if last_accessed:
            sql += "and created > :last_accessed "
            params['last_accessed'] = int(last_accessed)
        if platform:
            sql += "and coalesce(platform, :platform) = :platform "
            params['platform'] = platform
        if channel:
            sql += "and coalesce(channel, :channel) = :channel "
            params['channel'] = channel
        if lang:
            sql += "and coalesce(lang, :lang) = :lang "
            params['lang'] = lang
        if locale:
            sql += "and coalesce(locale, :locale) = :locale "
            params['locale'] = locale
        if idle_time:
            sql += "and coalesce(idle_time, :idle_time) = :idle_time "
            params['idle_time'] = idle_time
        sql += " order by id"
        items = self.engine.execute(text(sql), **dict(params))
        result = []
        for item in items:
            note = json.loads(item.note)
            note.update({'id': item.id})
            result.append(note)
        return {'snippets': result}

    def get_all(self, limit=None):
        result = []
        sql = 'select * from %s.%s ' % (self.__database__,
                self.__tablename__)
        if limit:
            sql += 'limit %d' % limit
        items = self.engine.execute(text(sql))
        for item in items:
            result.append(item)
        return result

