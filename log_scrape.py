import json
import time
import re
from campaign.storage import StorageBase
from sqlalchemy import (Column, Integer, String,
                        create_engine, MetaData, text, exc)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from campaign import logger, LOG
from datetime import datetime

Base = declarative_base()


class Scrapes(Base):
    __tablename__ = 'scrapes'

    id = Column('id', String(25), unique=True, primary_key=True)
    served = Column('served', Integer, server_default=text('0'))
    clicks = Column('clicks', Integer, server_default=text('0'))
    last = Column('last', Integer, index=True, server_default=text('0'))


class CounterException(Exception):
    pass


class Counter(StorageBase):
    __database__ = 'campaign'
    __tablename__ = 'scrapes'

    def __init__(self, config, **kw):
        try:
            super(Counter, self).__init__(config, **kw)
            self.metadata = MetaData()
            self._connect()
            #TODO: add the most common index.
        except Exception, e:
            logger.log(msg='Could not initialize Storage "%s"' % str(e),
                       type='error', severity=LOG.CRITICAL)
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
            logger.log(msg='Could not connect to db "%s"' % repr(e),
                       type='error', severity=LOG.EMERGENCY)
            raise e

    def increment(self, id, action, time):
        with self.engine.begin() as conn:
            action = re.sub(r'[^0-9A-Za-z]', '', action)
            try:
                conn.execute(text("insert into %s (id) values (:id)" %
                                  self.__tablename__), {'id': id})
            except exc.IntegrityError, e:
                pass
            try:
                print "%s marked as %s" % (id, action)
                conn.execute(text("update %s set %s=%s " % (
                    self.__tablename__, action, action) +
                    "+ 1, last=:time where id = :id and last <= :time"),
                    {'id': id,
                     'time': time})
            except Exception, e:
                import pdb; pdb.set_trace();

    def fetched(self, data, time):
        for item in data:
            if not 'url' in item:
                ##raise CounterException('Bad Data')
                print "Bad Data: %s" % str(item)
                return
            id = item.get('url').split('/').pop()
            self.increment(id, 'served', time)

    def redir(self, data, time):
        self.increment(data.get('id'), 'clicks', time)

    commands = {'redirect': redir,
                'fetched': fetched}

    def log(self, line):
        for command in self.commands.keys():
            if command + ' :' in line:
                dt = datetime.strptime(line.split(',')[0],
                                       '%Y-%m-%d %H:%M:%S')
                timestamp = int(time.mktime(dt.timetuple()))
                try:
                    data = json.loads(line.split(command + ' :')[1])
                    while (isinstance(data, basestring)):
                        data = json.loads(data)
                    self.commands.get(command)(self,
                                               data,
                                               timestamp)
                except Exception, e:
                    import pdb; pdb.set_trace()
                    raise e

    def parse(self, logfile):
        try:
            file = open(logfile, 'r')
            for line in file:
                self.log(line)
        except Exception, e:
            import pdb; pdb.set_trace()
            print str(e)
            pass

if __name__ == "__main__":

    from mozsvc.config import load_into_settings
    from pyramid.config import Configurator
    from campaign.resources import Root
    import sys

    settings = {}
    load_into_settings('campaign-local.ini', settings)
    filtered_settings = {}
    for key in settings.keys():
        if 'app.main.' in key:
            filtered_settings[key[9:]] = settings[key]
    config = Configurator(root_factory=Root, settings=filtered_settings)
    counter = Counter(config)
    for file in sys.argv[1:]:
        counter.parse(file)

