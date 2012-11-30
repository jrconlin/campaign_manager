# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Main entry point
"""
from pyramid.config import Configurator
from campaign.resources import Root
from mozsvc.config import load_into_settings
from mozsvc.middlewares import _resolve_name
from campaign.logger import Logging


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
    if sys.version_info[:3] < (2, 5, 0) or sys.version_info[:3] > (3, 0, 0):
        warnings.warn('Please run this code under version '
                      '2.6 or 2.7 of python.')
        bad |= True
    templatePath = os.path.join(os.path.dirname(__file__), 'templates',
                                'login.mako')
    if not os.path.exists(templatePath):
        warnings.warn(('Could not find required template. %s\n Your install ' %
                       templatePath) + 'may be corrupt. Please reinstall.')
        bad |= True
    if not config.registry['storage'].health_check():
        warnings.warn('Storage reported an error. Please check settings.')
        bad |= True
    if bad:
        raise Exception('Failing self diagnostic.')


def main(global_config, **settings):
    load_into_settings(global_config['__file__'], settings)
    config = Configurator(root_factory=Root, settings=settings)
    config.include("cornice")
    config.include("pyramid_beaker")
    config.include("mozsvc")
    config.scan("campaign.views")
    config.registry['storage'] = _resolve_name(
                                    settings.get('db.backend',
                                    'campaign.storage.sql.Storage'))(config)
    config.registry['auth'] = configure_from_settings('auth',
                                    settings['config'].get_map('auth'))
    config.registry['logger'] = Logging(config, global_config['__file__'])
    if settings.get('dbg.self_diag', False):
        self_diag(config)
    config.registry['logger'].log('Starting up', fields='',
                                  severity=LOG.INFORMATIONAL)
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
