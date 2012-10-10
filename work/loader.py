from sqlalchemy import (create_engine, MetaData, Table, Column,Integer, String, Text, Float, text)
from random import randint
from time import time
import string
import json
import math

ALPHABET = (string.digits + string.letters)

def as_id(num):
    if num == 0:
        return ALPHABET[0]
    barray = []
    base = len(ALPHABET)
    while num:
        remain = num % base
        num = num // base
        barray.append(ALPHABET[remain])
    barray.reverse()
    return ''.join(barray)


project = 'campaign'
dsn = 'mysql://snip:snip@localhost/%s' % project

engine = create_engine(dsn)

metadata = MetaData()

campaigns = Table('%ss' % project, metadata,
        Column('id', String(25), primary_key=True),
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
        Column('note', Text),
        Column('dest_url', Text))

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

query = """insert into %s.%ss (id, start_time, end_time, idle_time,
    lang, locale, channel, platform, version, created, author, note) values
    (:id, :start_time, :end_time, :idle_time, :lang, :locale, :channel,
     :platform, :version, :created, :author, :note);""" % (project, project)

for l in xrange(0,10000):
    r = randint(0,100)
    lang = picker(langs)
    locale = picker(locales)

    #this is semi-meaningless. It's based off of the creation time just
    # to limit collisions.
    while True:
        try:
            now = time()
            nowbits = math.modf(now)
            sig = "%s%s" % (as_id(int(nowbits[1])),
                    as_id(int(nowbits[0]*100000)))
            note = {'title': picker(titles), 'text': picker(texts)}
            note['url'] = 'https://%s.m.c/%s_%s/' % (project, lang,
                locale)

            engine.execute(text(query),
                id=sig,
                start_time=now,
                end_time=int(now + picker(offsets)),
                idle_time=int(3 + picker([0,1,2,4])),
                lang=lang,
                locale=locale,
                channel=picker(channels),
                platform=picker(platforms),
                version=picker(version),
                created=int(now + picker(offsets)),
                author=picker(authors),
                note=json.dumps(note))

        except Exception, e:
            print e
            continue
        break
