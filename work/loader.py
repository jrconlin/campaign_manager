from sqlalchemy import (create_engine, MetaData, Table, Column,Integer, String, Text, Float, text)
from random import randint
from time import time
from hashlib import md5
import json

project = 'campaign'
dsn = 'mysql://snip:snip@localhost/%s' % project

engine = create_engine(dsn)

metadata = MetaData()

campaigns = Table('%ss' % project, metadata,
        Column('id', Integer, autoincrement=True, primary_key=True),
        Column('start_time', Integer, index=True),
        Column('end_time', Integer, index=True),
        Column('idle_time', Integer, index=True),
        Column('lang', String(2), index=True),
        Column('locale', String(2), index=True),
        Column('channel', String(200), index=True),
        Column('platform', String(200), index=True),
        Column('version', Float, index=True),
        Column('created', Integer),
        Column('author', String(200)),
        Column('note', Text))

metadata.create_all(engine)

langs = ['en','es','pr', None]
locales = [None, 'us', 'ca', 'br']
offsets = [0, 86400, 604800, 31557600]
authors = ['alpha@example.com', 'beta@example.com', 'gamma@example.com', 'epsilon@example.com']
texts = ['text 1', 'text 2', 'text 3', 'text 4']
titles = ['Get Stuff!', 'Monkeys are awesome', 'Free Beer!', 'I Spit on your grave!']
channels = ['firefox', 'aurora', 'nightly', None ]
platforms = ['desktop', 'android', 'b2g', None]
version = ['14.1', '15.2', '16.0', None]

def picker(items):
    r = randint(0,100)
    if (r < 10):
        return items[3]
    elif (r < 30):
        return items[2]
    elif (r < 50):
        return items[1]
    else:
        return items[0]

query = """insert into %s.%ss (start_time, end_time, idle_time,
    lang, locale, channel, platform, version, created, author, note) values
    (:start_time, :end_time, :idle_time, :lang, :locale, :channel,
     :platform, :version, :created, :author, :note);""" % (project, project)

for l in xrange(0,10000):
    r = randint(0,100)
    now = int(time())
    lang = picker(langs)
    locale = picker(locales)

    sig = md5()
    note = {'title': picker(titles), 'text': picker(texts)}
    sig.update(('%s_%s:' % (lang, locale)) + json.dumps(note))

    note['url'] = 'https://%s.m.c/%s_%s/%s' % (project, lang,
            locale, sig.hexdigest())


    engine.execute(text(query),start_time=now,
        end_time=int(now + picker(offsets)),
        idle_time=int(now + picker(offsets)),
        lang=lang,
        locale=locale,
        channel=picker(channels),
        platform=picker(platforms),
        version=picker(version),
        created=int(now + picker(offsets)),
        author=picker(authors),
        note=json.dumps(note))

