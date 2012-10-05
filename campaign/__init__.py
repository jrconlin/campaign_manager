"""Main entry point
"""
from pyramid.config import Configurator
from metlog.config import client_from_stream_config
from campaign.resources import Root
from campaign.storage.sql import Storage
from mozsvc.config import load_into_settings
from mozsvc.middlewares import _resolve_name


def get_group(group_name, dictionary):
    if group_name is None:
        return dictionary
    else:
        result = {}
        trim = len(group_name) + 1
        for key in filter(lambda x: x.startswith(group_name), dictionary):
            result[key[trim:]] = dictionary[key]
        return result

def configure_from_settings(object_name, settings):
    config = dict(settings)
    if 'backend' not in config:
        if '%s.backend' % object_name in config:
            config = get_group(object_name, config)
    cls = _resolve_name(config.pop('backend'))
    return cls(**config)


def main(global_config, **settings):
    load_into_settings(global_config['__file__'], settings)
    config = Configurator(root_factory=Root, settings=settings)
    config.include("cornice")
    config.include("pyramid_beaker")
    config.include("mozsvc")
    config.scan("campaign.views")
    config.registry['storage'] = Storage(config)
    config.registry['auth'] = configure_from_settings('auth',
            settings['config'].get_map('auth'))
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
