#!/usr/bin/env python3
"""
Install valedictory using setuptools
"""

from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    readme = f.read()

with open('valedictory/version.py', 'r') as f:
    version_string = None
    exec(f.read())
    assert version_string is not None


setup(
    name='valedictory',
    version=version_string,
    description='Validate dicts against a schema',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@timheap.me',
    url='https://github.com/timheap/valedictory/',
    project_urls={
        "Bug Tracker": 'https://github.com/timheap/valedictory/issues',
        "Documentation": 'https://valedictory.readthedocs.io',
        "Source Code": 'https://github.com/timheap/valedictory',
    },

    install_requires=[
        'aniso8601~=3.0.0',
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
