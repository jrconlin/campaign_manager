"""Main entry point
"""
from pyramid.config import Configurator
from campaign.resources import Root
from campaign.storage.sql import Storage


def main(global_config, **settings):
    config = Configurator(root_factory=Root, settings=settings)
    config.include("cornice")
    config.scan("campaign.views")
    config.registry['storage'] = Storage(config)
    return config.make_wsgi_app()
