import logging
import json


METLOG = False
BOTO = False
try:
    from metlog.config import client_from_stream_config
    METLOG = True
except ImportError:
    pass
try:
    import boto
    import uuid
    from time import time
    BOTO = True
except ImportError:
    pass


class LoggingException(Exception):
    pass


class Logging(object):
    metlog2log = [logging.CRITICAL, logging.CRITICAL, logging.CRITICAL,
                  logging.ERROR, logging.WARNING, logging.INFO,
                  logging.INFO, logging.DEBUG]

    metlog = None
    boto = None

    def __init__(self, config, settings_file):
        global METLOG, BOTO
        settings = config.get_settings()
        self.logger = logging.getLogger(
            settings.get('logging.name', 'campaign-manager'))
        self.logger.level = 1
        if METLOG and settings.get('logging.use_metlog', True):
            self.metlog = client_from_stream_config(
                open(settings_file, 'r'),
                'metlog')
        else:
            METLOG = False
        if BOTO:
            try:
                self.boto = boto.connect_sdb(settings.get('aws.key'),
                                             settings.get('aws.secret')).\
                    lookup(settings.get('aws.domain'))
            except Exception, e:
                import pdb; pdb.set_trace()
                BOTO = False

    def log(self, msg=None, type='event', severity=7,
            fields=None):
        self.logger.log(self.metlog2log[severity],
                        "%s : %s", msg, json.dumps(fields))
        if self.metlog:
            self.metlog.metlog(type, severity, payload=msg, fields=fields)
        if self.boto:
            rec = self.boto.new_item(uuid.uuid1())
            rec['type'] = type
            rec['severity'] = severity
            rec['payload'] = msg
            rec['fields'] = json.dumps(fields)
            rec['created'] = time()
            rec.save()


