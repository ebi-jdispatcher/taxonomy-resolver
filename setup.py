#!/usr/bin/env python
# -*- coding: utf-8

"""
NCBI Taxonomy Resolver

:copyright: (c) 2020.
:license: Apache 2.0, see LICENSE for more details.
"""

import os
from setuptools import setup, find_packages

from taxonresolver import __version__, __author__, __email__


def gather_dependencies():
    with open('requirements.txt', 'r') as f_in:
        return [l for l in f_in.read().rsplit(os.linesep)
                if l and not l.startswith("#")]


DEPENDENCIES = gather_dependencies()

setup(
    # Basic package information.
    name='taxonresolver',
    version=__version__,
    packages=find_packages(),

    # Packaging options.
    package_data={'taxonresolver': ['testdata/*']},
    include_package_data=True,
    py_modules=['taxonresolver'],

    # Package dependencies.
    install_requires=DEPENDENCIES,
    test_requires=['pytest', 'python_version>"3.7"'],

    extras_require={
        'fastcache': ['fastcache>=1.1.0']
    },

    # Tests.
    test_suite='tests',

    # Metadata for PyPI.
    author=__author__,
    author_email=__email__,
    license='LICENSE',
    entry_points={
        "console_scripts": ["taxonomy_resolver=taxonresolver.cli:cli"]
    },
    url='https://gitlab.ebi.ac.uk/ebi-biows/taxonomy-resolver',
    download_url="https://gitlab.ebi.ac.uk/ebi-biows/taxonomy-resolver/-/archive/master/taxonomy-resolver-master.zip",
    keywords='bioinformatics ncbi taxonomy python anytree',
    description=('Taxonomy Resolver builds NCBI Taxonomy Trees and lists of '
                 'Taxonomy Identifiers (TaxIDs) based on the NCBI Taxonomy Database.'),
    long_description=open('README.rst').read(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
    ]
)
