# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#from campaign import logger, LOG
from email import utils as eut
import calendar
import string

ALPHABET = (string.digits + string.letters)


def strToUTC(datestr):
    # Logging and trapping this error causes circular dependencies
    secs = 0
    timet = eut.parsedate_tz(datestr)
    secs = int(calendar.timegm(timet[:8])) + timet[9]
    return secs


def as_id(num):
    if num == 0:
        return ALPHABET[0]
    barray = []
    base = len(ALPHABET)
    while num:
        remain = num % base
        num = num // base
        barray.append(ALPHABET[remain])
    barray.reverse()
    return ''.join(barray)


def from_id(id):
    base = len(ALPHABET)
    strlen = len(id)
    num = 0
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += ALPHABET.index(char) * (base ** power)
        idx += 1
    return num


def strToBool(s="False"):
    if type(s) == bool:
        return s
    return s.lower() in ["true", "1", "yes", "t"]
