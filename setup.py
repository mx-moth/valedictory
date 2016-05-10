#!/usr/bin/env python3
"""
Install valedictory using setuptools
"""

from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    readme = f.read()

with open('valedictory/version.py', 'r') as f:
    version = None
    exec(f.read())


setup(
    name='valedictory',
    version=version,
    description='Validate dicts against a schema',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@timheap.me',
    url='https://bitbucket.org/tim_heap/valedictory/',

    install_requires=[
        'iso8601==0.1.11',
    ],
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
