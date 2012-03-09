#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='swift_usage',
    version='0.1',
    description='Swift usage API based on the slogging data. (includes slogging processor)',
    classifiers=['Programming Language :: Python'],
    keywords='swift_usage slogging swift usage rest api openstack',
    author='CloudOps / Will Stevens (swill)',
    author_email='wstevens@cloudops.com',
    packages=find_packages(),
)