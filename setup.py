# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
""" Setup file.
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


setup(name='campaign',
    version=1.000,
    description='campaign',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    keywords="web services",
    author='jr conlin',
    author_email='jrconlin@mozilla.com',
    url='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['cornice', 'PasteScript'],
    entry_points = """\
    [paste.app_factory]
    main = campaign:main
    """,
    paster_plugins=['pyramid'],
)
