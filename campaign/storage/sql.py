import logging
import json
import time
from . import StorageBase, StorageException
from sqlalchemy import (Column, Integer, String, Text,
                        create_engine, MetaData, text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


Base = declarative_base()


class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column('id', String(25), primary_key=True)
    priority = Column('priority', Integer, index=True)
    specific = Column('specific', Integer, index=True)
    channel = Column('channel', String(24), index=True, nullable=True)
    version = Column('version', String(30), index=True, nullable=True)
    product = Column('product', String(50), index=True, nullable=True)
    platform = Column('platform', String(50), index=True, nullable=True)
    lang = Column('lang', String(24), index=True, nullable=True)
    locale = Column('locale', String(24), index=True, nullable=True)
    start_time = Column('start_time', Integer, index=True)
    end_time = Column('end_time', Integer, index=True, nullable=True)
    idle_time = Column('idle_time', Integer, index=True, nullable=True)
    note = Column('note', Text)
    dest_url = Column('dest_url', Text)
    author = Column('author', String(255), index=True)
    created = Column('created', Integer, index=True)


class Storage(StorageBase):
    __database__ = 'campaign'
    __tablename__ = 'campaigns'

    def __init__(self, config, **kw):
        try:
            super(Storage, self).__init__(config, **kw)
            self.metadata = MetaData()
            self._connect()
            #TODO: add the most common index.
        except Exception, e:
            logging.error('Could not initialize Storage "%s"', str(e))
            raise e

    def _connect(self):
        try:
            userpass = ''
            host = ''
            if (self.settings.get('db.user')):
                userpass = '%s:%s@' % (self.settings.get('db.user'),
                                       self.settings.get('db.password'))
            if (self.settings.get('db.host')):
                host = '%s' % self.settings.get('db.host')
            dsn = '%s://%s%s/%s' % (self.settings.get('db.type', 'mysql'),
                                    userpass, host,
                                    self.settings.get('db.db',
                                        self.__database__))
            self.engine = create_engine(dsn, pool_recycle=3600)
            Base.metadata.create_all(self.engine)
            self.session = scoped_session(sessionmaker(bind=self.engine))()
            #self.metadata.create_all(self.engine)
        except Exception, e:
            logging.error('Could not connect to db "%s"' % repr(e))
            raise e

    def health_check(self):
        try:
            healthy = True
            with self.engine.begin() as conn:
                conn.execute(("insert into %s " % self.__tablename__) +
                    "(id, product, channel, platform, start_time, end_time, " +
                    "note, dest_url, author, created) " +
                    "values ('test', 'test', 'test', 'test', 0, 0, 'test', " +
                    "'test', 'test', 0)")
                resp = conn.execute(("select id, note from %s where " %
                                    self.__tablename__) + "id='test';")
                if resp.rowcount == 0:
                    healthy = False
                conn.execute("delete from %s where id='test';" %
                             self.__tablename__)
        except Exception, e:
            import warnings
            warnings.warn(str(e))
            return False
        return healthy

    def resolve(self, token):
        if token is None:
            return None
        sql = 'select * from campaigns where id = :id'
        items = self.engine.execute(text(sql), {'id': token})
        row = items.fetchone()
        if items.rowcount == 0 or row is None:
            return None
        result = dict(zip(items.keys(), row))
        return result

    def put_announce(self, data):
        if data.get('note') is None:
            raise StorageException('Incomplete record. Skipping.')
        specificity = 0
        for col in ['lang', 'loc', 'platform',
                    'channel', 'version']:
            if len(str(data.get(col,''))):
                specificity += 1
        if data.get('idle_time') and int(data.get('idle_time')) != 0:
            specificity += 1
        data['specific'] = specificity
        snip = self.normalize_announce(data)
        campaign = Campaign(**snip)
        self.session.add(campaign)
        self.session.commit()
        return self

    def get_announce(self, data):
        # Really shouldn't allow "global" variables, but I know full well
        # that they're going to want them.
        params = {}
        # The window allows the db to cache the query for the length of the
        # window. This is because the database won't cache a query if it
        # differs from a previous one. The timestamp will cause the query to
        # not be cached.
        window = int(self.settings.get('db.query_window', 1))
        if window == 0:
            window = 1
        now = int(time.time() / window)
        sql = ("select id, note, priority, `specific`, "
               "created from %s where " % self.__tablename__ +
               " coalesce(round(start_time / %s), %s) < %s " % (window,
               now - 1, now) +
               "and coalesce(round(end_time / %s), %s) > %s " % (window,
               now + 1, now))
        if data.get('last_accessed'):
            sql += "and created > :last_accessed "
            params['last_accessed'] = int(data.get('last_accessed'))
        for field in ['product', 'platform', 'channel', 'version', 'lang',
                      'locale']:
            if data.get(field):
                sql += "and coalesce(%s, :%s) = :%s " % (field, field, field)
                params[field] = data.get(field)
        if not data.get('idle_time'):
            data['idle_time'] = 0
        sql += "and coalesce(idle_time, 0) <= :idle_time "
        params['idle_time'] = data.get('idle_time')
        # RDS doesn't like multiple order bys, sqllite doesn't like concat.
        sql += " order by priority desc, `specific` desc, created desc"
        if (self.settings.get('dbg.show_query', False)):
            print sql
            print params
        if (self.settings.get('db.limit')):
            sql += " limit :limit"
            params['limit'] = self.settings.get('db.limit')
        items = self.engine.execute(text(sql), **dict(params))
        result = []
        for item in items:
            note = json.loads(item.note)
            note.update({
                # ID in this case is a unique integer per CM record
                # it is used by the client to replace records.
                'id': int(item.created * 100),
                # This uses the server string ID for redirect/tracking
                'url': self.settings.get('redir.url', 'http://%s/%s%s') % (
                        self.settings.get('redir.host', 'localhost'),
                        self.settings.get('redir.path', 'redirect/'),
                        item.id)})
            result.append(note)
        return result

    def get_all_announce(self, limit=None):
        result = []
        sql = 'select * from %s order by created desc ' % self.__tablename__
        if limit:
            sql += 'limit %d' % limit
        items = self.engine.execute(text(sql))
        for item in items:
            result.append(item)
        return result

    def del_announce(self, keys):
        #TODO: how do you safely do an "in (keys)" call?
        sql = 'delete from %s where id = :key' % self.__tablename__
        for key in keys:
            self.engine.execute(text(sql), {"key": key})
        self.session.commit()

    def purge(self):
        sql = 'delete from %s;' % self.__tablename__
        self.engine.execute(text(sql))
        self.session.commit()
