# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Main entry point
"""
import logging

from pyramid.config import Configurator
from metlog.config import client_from_stream_config
from campaign.resources import Root
from campaign.storage.sql import Storage
from mozsvc.config import load_into_settings
from mozsvc.middlewares import _resolve_name

logger = logging.getLogger('campaign')


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

def self_diag(config):
    import warnings
    import sys
    import os
    bad = False
    vernum = sys.version.split(' ')[0]
    if not (vernum.startswith('2.6') or vernum.startswith('2.7')):
        warnings.warn('Please run this code under version '
                '2.6 or 2.7 of python.');
        bad |= True
    templatePath = os.path.join(os.path.dirname(__file__), 'templates',
            'login.mako')
    if not os.path.exists(templatePath):
        warnings.warn('Could not find required template. Your install '
                'may be corrupt. Please reinstall.');
        bad |= True
    if not config.registry['storage'].health_check():
        warnings.warn('Storage reported an error. Please check settings.');
        bad |= True



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
    if settings.get('dbg.self_diag', False):
        self_diag(config)
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
