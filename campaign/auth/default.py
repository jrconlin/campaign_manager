# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from pyramid.security import authenticated_userid


class DefaultAuth(object):

    def get_user_id(self, request):
        return authenticated_userid(request)
