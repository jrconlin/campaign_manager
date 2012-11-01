# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pyramid.security import Everyone, Authenticated, Allow


class Root(object):

    __acl__ = [
        (Allow, Everyone, "view"),
        (Allow, Authenticated, "authenticated"),
    ]

    def __init__(self, request):
        self.request = request
