# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class TConfig:

    def __init__(self, data):
        self.settings = data

    def get_settings(self):
        return self.settings


