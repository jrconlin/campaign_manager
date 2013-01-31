from email import utils as eut
from . import logger, LOG
import calendar


def strToUTC(datestr):
    secs = 0
    try:
        timet = eut.parsedate_tz(datestr)
        secs = int(calendar.timegm(timet[:8])) + timet[9]
    except Exception, e:
        if logger:
            logger.log(type='campaign',
                       severity=LOG.ERROR,
                       msg=repr(e) + str(datestr),
                       fields={})
    return secs
