#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python AFSK Module Constants."""

import logging
import math
import os

__author__ = 'Christopher H. Casebeer <c@chc.name>'
__copyright__ = 'Copyright 2013 Christopher H. Casebeer. All rights reserved.'
__license__ = 'Simplified BSD License'


if bool(os.environ.get('DEBUG_ALL')) or bool(os.environ.get('DEBUG_AFSK')):
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

LOG_FORMAT = logging.Formatter(
    ('%(asctime)s afsk %(levelname)s %(name)s.%(funcName)s:%(lineno)d - '
     '%(message)s'))

MARK_HZ = 1200.0
SPACE_HZ = 2200.0
BAUD_RATE = 1200.0
TWO_PI = 2.0 * math.pi

DEFAULT_DESTINATION = b'APYSAF'
DEFAULT_TEXT = b'Python AFSK Module'
