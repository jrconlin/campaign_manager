"""Main entry point
"""
from pyramid.config import Configurator
from metlog.config import client_from_stream_config
from campaign.resources import Root
from campaign.storage.sql import Storage


def main(global_config, **settings):
    config = Configurator(root_factory=Root, settings=settings)
    config.include("cornice")
    config.scan("campaign.views")
    config.registry['storage'] = Storage(config)
    metlog_client = client_from_stream_config(
            open(global_config['__file__'], 'r'),
            'metlog')
    config.registry['metlog'] = metlog_client
    return config.make_wsgi_app()


class LOG:
    EMERGENCY = 0
    ALERT = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = 4
    NOTICE = 5
    INFORMATIONAL = 6
    DEBUG = 7
