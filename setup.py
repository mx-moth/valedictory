#!/usr/bin/env python3
"""
Install valedictory using setuptools
"""

from setuptools import setup, find_packages

from valedictory import __version__

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='valedictory',
    version=__version__,
    description='Validate dicts against a schema',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@timheap.me',
    url='https://bitbucket.org/tim_heap/valedictory/',

    install_requires=[],
    zip_safe=False,
    license='BSD License',

    packages=find_packages(),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
