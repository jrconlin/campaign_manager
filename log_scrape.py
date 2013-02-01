from campaign.storage.metrics import Counter
from datetime import date
import time


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
    yesterday = date.fromtimestamp(time.time() - 86400).isoformat()
    files = sys.argv[1:] or ['logs/campaign.log.' + yesterday]
    for file in files:
        counter.parse(file)

