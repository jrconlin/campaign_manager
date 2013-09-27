from campaign.logger import LOG
from campaign.storage import StorageBase
from datetime import datetime
from sqlalchemy import (Column, Integer, String,
                        MetaData, text)
from sqlalchemy.ext.declarative import declarative_base
import json
import re
import time


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

    def __init__(self, config, logger, **kw):
        try:
            super(Counter, self).__init__(config, **kw)
            self.logger = logger
            self.metadata = MetaData()
            self._connect()
            #TODO: add the most common index.
        except Exception, e:
            logger.log(msg='Could not initialize Storage "%s"' % str(e),
                       type='error', severity=LOG.CRITICAL)
            raise e

    def bulk_increment(self, conn, id, action, time=time.time()):
        action = re.sub(r'[^0-9A-Za-z]', '', action)
        try:
            if (self.settings.get("db.type") == "sqlite"):
                conn.execute(text("insert or ignore into " +
                                  self.__tablename__ +
                                  " (id)" +
                                  " values (:id ); "),
                             {"id": id})
            else:
                dml = text("insert into " + self.__tablename__
                           + " (id, %s) values (:id, 1) " % action
                           + " on duplicate key update %s=%s+1, last=:last;"
                           % (action, action))
                conn.execute(dml, {"id": id, "last": time})
        except Exception, e:
            self.logger.log(msg="Could not increment id: %s" % str(e),
                            type="error", severity=LOG.ERROR)

    def increment(self, id, action, time):
        with self.engine.begin() as conn:
            self.bulk_increment(conn, id, action, time)

    def fetched(self, data, time=time.time()):
        with self.engine.begin() as conn:
            for item in data:
                self.bulk_increment(conn, item.get('token'), 'served', time)

    def redir(self, data, time=time.time()):
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
                    self.logger.log(msg="Could not log %s" % str(e),
                                    type="error", severity=LOG.ERROR)
                    raise e

    def report(self, id):
        with self.engine.begin() as conn:
            resp = conn.execute(text(("select * from %s " %
                                      self.__tablename__) +
                                     "where id = :id"), {'id': id})
            if resp.rowcount > 0:
                result = resp.fetchone()
                return dict(zip(resp.keys(), result))
            else:
                return {}

    def parse(self, logfile):
        try:
            file = open(logfile, 'r')
            for line in file:
                self.log(line)
        except Exception, e:
            self.logger.log(msg="Could not parse %s" % str(e),
                            type="error", severity=LOG.ERROR)
            pass

