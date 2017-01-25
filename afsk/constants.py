#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python AFSK Module Constants."""

import logging
import math

__author__ = 'Christopher H. Casebeer <c@chc.name>'
__copyright__ = 'Copyright 2013 Christopher H. Casebeer. All rights reserved.'
__license__ = 'Simplified BSD License'


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = logging.Formatter(
    ('%(asctime)s afsk %(levelname)s %(name)s.%(funcName)s:%(lineno)d - '
     '%(message)s'))

MARK_HZ = 1200.0
SPACE_HZ = 2200.0
BAUD_RATE = 1200.0
TWO_PI = 2.0 * math.pi

DEFAULT_DESTINATION = b'APRS'
DEFAULT_DIGIPEATERS = b'WIDE1-1'
DEFAULT_INFO = b'Test Info'
