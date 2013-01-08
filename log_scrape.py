from campaign.storage.metrics import Counter


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

