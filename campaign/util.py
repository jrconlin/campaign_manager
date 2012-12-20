from email import utils as eut
import calendar


def strToUTC(datestr):
    secs = 0
    try:
        timet = eut.parsedate_tz(datestr)
        secs = int(calendar.timegm(timet[:8])) + timet[9]
    except Exception, e:
        import pdb; pdb.set_trace();
    return secs
