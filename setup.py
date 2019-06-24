# -*- coding: utf-8 -*-

#!/bin/env python

# MIT License

# Copyright (c) 2019, Marco Marzetti <marco@lamehost.it>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""Install package"""


import codecs
import sys

from os.path import abspath, dirname, join
from setuptools import setup


ABOUT = dict()
with open("aggregate_prefixes/__about__.py") as _:
    exec(_.read(), ABOUT)

HERE = abspath(dirname(__file__))
with codecs.open(join(HERE, 'README.md'), encoding='utf-8') as f:
    README = f.read()

setup(
    name='aggregate_prefixes',
    author=ABOUT['__author__'],
    author_email=ABOUT['__author_email__'],
    description=ABOUT['__description__'],
    license=ABOUT['__license__'],
    url=ABOUT['__url__'],
    version=ABOUT['__version__'],
    packages=['aggregate_prefixes'],
    setup_requires=["nose", "coverage", "mock"],
    install_requires=["ipaddress"] if sys.version_info.major == 2 else [],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'aggregate-prefixes = aggregate_prefixes.__main__:main',
        ],
    },
    long_description=README,
    long_description_content_type='text/markdown',
    zip_safe=False,
    test_suite='nose.collector'
)
