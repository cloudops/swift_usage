#!/usr/bin/env python
# Copyright (c) 2011-2012 CloudOps
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
from swift_usage import __version__ as version

name = 'swift_usage'

setup(
    name=name,
    version=version,
    description='Swift usage API based on the slogging data. (includes slogging processor)',
    license='Apache License (2.0)',
    classifiers=['Programming Language :: Python'],
    keywords='swift_usage slogging swift usage rest api openstack',
    author='CloudOps / Will Stevens (swill)',
    author_email='wstevens@cloudops.com',
    packages=find_packages(),
    install_requires=['bottle', 'pymongo'],
    scripts=['swift_usage/slogging_processor', 'swift_usage/swift_usage_service']
)