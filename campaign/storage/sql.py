import json
import time
import uuid
from . import StorageBase, StorageException, Base
from .metrics import Counter
from campaign.logger import LOG
from campaign.views import api_version
from sqlalchemy import (Column, Integer, String, Text, text)


class Users(Base):
    __tablename__ = 'users'
    email = Column('email', String(100), primary_key=True)
    id = Column('id', String(32), index=True)
    sponsor = Column('sponsor', String(100))
    time = Column('date', Integer)
    level = Column('level', Integer)


class Campaign(Base):
    __tablename__ = 'campaigns'

    # Due to a miscommunication during design, the client was
    # created requiring the 'id' to be a numeric. We use 'id' as
    # a unique identifier string.
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
    title = Column('title', String(50))
    status = Column('status', Integer)


class Storage(StorageBase):
    __database__ = 'campaign'
    __tablename__ = 'campaigns'

    def __init__(self, config, logger, **kw):
        try:
            super(Storage, self).__init__(config, **kw)
            self.logger = logger
            self._connect()
            # Store off a link to the main table.
            self.campaigns = Base.metadata.tables.get(Campaign.__tablename__)
            self.users = Base.metadata.tables.get(Users.__tablename__)
            self.counter = Counter(config, logger, **kw)
            #TODO: add the most common index.
        except Exception, e:
            logger.log(msg='Could not initialize Storage "%s"' % str(e),
                       type='error', severity=LOG.CRITICAL)
            raise e

    def health_check(self):
        try:
            healthy = True
            with self.engine.begin() as conn:
                ins = self.campaigns.insert().values(
                    id="test",
                    product="test",
                    channel="test",
                    platform="test",
                    start_time=0,
                    end_time=0,
                    note="test",
                    dest_url="test",
                    author="test",
                    created=0)
                conn.execute(ins)
                sel = self.campaigns.select(self.campaigns.c.id == "test")
                resp = conn.execute(sel)
                rows = resp.fetchall()
                if not len(rows):
                    healthy = False
                conn.execute(self.campaigns.delete(self.campaigns.c.id ==
                                                   "test"))
        except Exception, e:
            import warnings
            warnings.warn(str(e))
            return False
        return healthy

    def resolve(self, token):
        if token is None:
            return None
        sel = self.campaigns.select(self.campaigns.c.id == token)
        items = self.engine.execute(sel)
        row = items.fetchone()
        if row is None:
            return None
        result = dict(zip(items.keys(), row))
        return result

    def put_announce(self, data, sessionHandle=None, now=None):
        if sessionHandle:
            session = sessionHandle
        else:
            session = self.Session()
        if isinstance(data, list):
            for item in data:
                self.put_announce(item, session, now)
            return self
        if data.get('body') is None:
            raise StorageException('Incomplete record. Skipping.')
        specificity = 0
        for col in ['lang', 'loc', 'platform',
                    'channel', 'version']:
            if len(str(data.get(col, ''))):
                specificity += 1
        if data.get('idle_time') and int(data.get('idle_time')) != 0:
            specificity += 1
        data['specific'] = specificity
        snip = self.normalize_announce(data, now)
        campaign = Campaign(**snip)

        session.add(campaign)
        session.commit()
        if not sessionHandle:
            session.flush()
            session.close()
        return self

    def get_announce(self, data, now=None):
        # Really shouldn't allow "global" variables, but I know full well
        # that they're going to want them.
        params = {}
        # The window allows the db to cache the query for the length of the
        # window. This is because the database won't cache a query if it
        # differs from a previous one. The timestamp will cause the query to
        # not be cached.
        #window = int(self.settings.get('db.query_window', 1))
        window = 1
        if now is None:
            now = int(time.time() / window) * window
        # Using raw sql here for performance reasons.
        sql = ("select created, id, note, priority, `specific`, "
               "start_time, idle_time from %s where " % self.__tablename__ +
               " coalesce(cast(start_time as unsigned), %s) <= %s"
               % (now - 1, now))
        for field in ['product', 'platform', 'channel', 'lang', 'locale']:
            if data.get(field):
                sql += " and coalesce(%s, :%s) = :%s " % (field, field, field)
                params[field] = data.get(field)
        data['idle_time'] = data.get('idle', 0)
        try:
            if 'version' in data:
                sql += " and coalesce(version, :version) =  :version"
                params['version'] = str(data['version']).split('.')[0]
        except Exception:
            pass
        sql += " and coalesce(idle_time, 0) <= :idle_time "
        params['idle_time'] = data.get('idle_time')
        sql += " order by priority desc, `specific` desc, start_time desc"
        if (self.settings.get('dbg.show_query', False)):
            print sql
            print params
        if (self.settings.get('db.limit')):
            sql += " limit :limit"
            params['limit'] = self.settings.get('db.limit')
        try:
            items = self.engine.execute(text(sql), **dict(params))
        except Exception, e:
            self.logger.log(msg='SQL Error "%s" ' % str(e),
                            type='error', severity=LOG.CRITICAL)
        result = []
        for item in items:
            # last_accessed may be actually set to 'None'
            last_accessed = int(data.get('last_accessed') or '0')
            if last_accessed:
                start = item.start_time or item.created
                if (item.idle_time and
                        last_accessed > start + (86400 * item.idle_time)):
                        continue
                else:
                    if last_accessed > start:
                        continue
            note = json.loads(item.note)
            note.update({
                # ID in this case is a unique integer per CM record
                # it is used by the client to replace records.
                'id': int(item.created * 100),
                # token is stripped before being sent to the client.
                # it's used for metrics tracking.
                'token': item.id,
                'created': item.created,
                # This uses the server string ID for redirect/tracking
                'url': self.settings.get('redir.url', 'http://%s/%s%s') % (
                        self.settings.get('redir.host', 'localhost'),
                        self.settings.get('redir.path',
                                          'redirect/%s/' % api_version),
                        item.id)})
            result.append(note)
        return result

    def get_all_announce(self, limit=None):
        result = []
        sql = ("select c.*,s.served,s.clicks from " +
               "(campaigns as c left join scrapes " +
               "as s on c.id=s.id) order by created desc ")
        if limit:
            sql += 'limit %d' % limit
        items = self.engine.execute(text(sql))
        for item in items:
            counter = self.counter.report(item.id)
            ann = dict(item)
            ann.update(counter)
            result.append(ann)
        return result

    def del_announce(self, keys):
        #TODO: how do you safely do an "in (keys)" call?
        session = self.Session()
        sql = 'delete from %s where id = :key' % self.__tablename__
        for key in keys:
            self.engine.execute(text(sql), {"key": key})
        session.commit()

    def purge(self):
        session = self.Session()
        sql = 'delete from %s;' % self.__tablename__
        self.engine.execute(text(sql))
        session.commit()

    def user_health_check(self):
        #foo
        try:
            uid = self.add_user('test', '', 0)
            self.rm_user(uid)
            # with self.engine.begin() as conn:
        except Exception, e:
            import warnings
            warnings.warn(str(e))
            return False
        return True

    def is_user(self, email):
        sel = self.users.select(self.users.c.email == email)
        items = self.engine.execute(sel)
        row = items.fetchone()
        if row is None:
            return False
        return True

    def user_list(self):
        result = []
        sql = "select * from users order by email"
        items = self.engine.execute(text(sql))
        for item in items:
            result.append(dict(item))
        return result

    def add_user(self, email, sponsor, level=0):
        try:
            uid = uuid.uuid4().hex
            with self.engine.begin() as conn:
                ins = self.users.insert().values(
                    id=uid,
                    email=email,
                    sponsor=sponsor,
                    level=level,
                    date=int(time.time()))
                conn.execute(ins)
            return uid
        except Exception, e:
            self.logger.log(msg='Could not add user "%s", "%s"' %
                            (email, repr(e)),
                            type="error", severity=LOG.ERROR)
            return None

    def rm_user(self, id):
        if len(id) == 0 or id == '0':
            return False
        try:
            with self.engine.begin() as conn:
                rm = self.users.delete().where(self.users.c.id == id)
                conn.execute(rm)
                return True
        except Exception, e:
            self.logger.log(msg='Could not delete user with id "%s", "%s"' %
                            (id, repr(e)),
                            type="error", severity=LOG.ERROR)
        return False
