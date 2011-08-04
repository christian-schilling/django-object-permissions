#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='django-object-permissions',
    version='0.0.1',
    description='per object permissions for Django',
    author='Christian Schilling',
    author_email='initcrash@gmail.com',
    url='http://github.com/initcrash/django-object-permissions/',
    download_url='http://github.com/initcrash/django-object-permissions/downloads',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    packages=[ 'object_permissions', ],
)

