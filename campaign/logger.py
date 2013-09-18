import logging
import json


class LOG:
    EMERGENCY = 0
    ALERT = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = WARN = 4
    NOTICE = 5
    INFORMATIONAL = INFO = 6
    DEBUG = 7


HEKA = False
BOTO = False
try:
    from heka.config import client_from_stream_config
    HEKA = True
except ImportError:
    pass


class LoggingException(Exception):
    pass


class Logging(object):
    metlog2log = [logging.CRITICAL, logging.CRITICAL, logging.CRITICAL,
                  logging.ERROR, logging.WARNING, logging.INFO,
                  logging.INFO, logging.DEBUG]

    heka = None
    boto = None
    loggername = 'campaign-manager'

    def __init__(self, config, settings_file):
        global HEKA, BOTO
        settings = config.get_settings()
        self.loggername = settings.get('logging.name', 'campaign-manager')
        self.logger = logging.getLogger(self.loggername)
        self.logger.level = 1
        if HEKA and settings.get('logging.use_heka', True):
            self.heka = client_from_stream_config(
                open(settings_file, 'r'),
                'heka')
        else:
            HEKA = False

    def log(self, msg=None, etype='event', severity=7,
            fields=None):
        self.logger.log(severity,
                        "%s [%d] %s : %s", self.loggername,
                        severity, msg, json.dumps(fields))
        if self.heka:
            if (fields is not None and
                    type(fields) is not dict):
                if len(fields) == 0:
                    fields = None
                else:
                    fields = {"value": fields}
            self.heka.heka(type=etype,
                           logger=self.loggername,
                           severity=severity,
                           payload=msg,
                           fields=fields)
