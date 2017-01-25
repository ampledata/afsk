#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for the Python AFSK Module.

Source:: https://github.com/casebeer/afsk
"""

import os
import setuptools
import sys

__title__ = 'afsk'
__version__ = '0.0.4b1'
__author__ = 'Christopher H. Casebeer <c@chc.name>'
__copyright__ = 'Copyright (c) 2013 Christopher H. Casebeer. All rights reserved.'
__license__ = 'Simplified BSD License'


def publish():
    """Function for publishing package to pypi."""
    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist')
        os.system('twine upload dist/*')
        sys.exit()


publish()


setuptools.setup(
    name=__title__,
    version=__version__,
	description=u"Bell 202 Audio Frequency Shift Keying encoder and APRS packet audio tools",
	author='Christopher H. Casebeer',
	author_email="",
	url='https://github.com/casebeer/afsk',
	install_requires=[
		'audiogen',
		'bitarray'
	],
	extras_require={
		'soundcard_output': ['PyAudio']
	},
	tests_require=['nose', 'crc16'],
	test_suite='nose.collector',
	entry_points={
		'console_scripts': [
			'aprs = afsk.cmd:cli'
		]
	},
	long_description=open('LICENSE').read().decode('utf8'),
    zip_safe=False,
    packages=['afsk'],
    package_data={'': ['LICENSE']},
    package_dir={'afsk': 'afsk'},
    license=open('LICENSE').read().decode('utf8'),
    include_package_data=True,
    keywords=[
        'Ham Radio', 'APRS', 'AFSK'
    ],
	classifiers=[
		"Environment :: Console",
		"License :: OSI Approved :: BSD License",
		"Programming Language :: Python :: 2.7",
		"Intended Audience :: Developers",
		"Intended Audience :: End Users/Desktop",
		"Topic :: Multimedia :: Sound/Audio",
		"Topic :: Communications :: Ham Radio",
	]
)
